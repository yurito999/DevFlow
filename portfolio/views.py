from portfolio.models import Portfolio, Formacao, ExperienciaTrabalho, Instituicao, Curso  # Importa os modelos
from portfolio.forms import PortfolioForm, FormacaoFormSet, ExperienciaTrabalhoFormSet, CursoForm  # Importa os formulários
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test  # Importa os decoradores de autenticação
from django.utils.decorators import method_decorator  # Permite decorar as views baseadas em classe
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView  # Importa as views genéricas
from django.shortcuts import redirect, get_object_or_404, render  # Ferramentas para redirecionamento e renderização de templates
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Q


# ==============================================
# Verifica se o usuário é administrador
# ==============================================
def admin_check(user):
    return user.is_superuser


# ==============================================
# Método da barra de busca de portfólios
# ==============================================
def search_profiles(request):
    query = request.GET.get('q', '')
    if query:
        profiles = Portfolio.objects.filter(primeiro_nome__icontains=query)[:5]
        profiles_list = []
        for profile in profiles:
            profiles_list.append({
                'nome': f"{profile.primeiro_nome} {profile.sobrenome}",
                'principal_formacao': profile.principal_formacao,
                'url': f"/portfolio/{profile.pk}/",
                'photo_url': profile.photo.url if profile.photo else None  # Adicionando URL da foto
            })
        return JsonResponse(profiles_list, safe=False)
    return JsonResponse([], safe=False)


# ==============================================
# Listar portfólios cadastrados com paginação e animação
# ==============================================
class PortfolioListView(ListView):
    model = Portfolio
    template_name = 'portfolio.html'
    context_object_name = 'portfolios'
    paginate_by = 8

    def get_queryset(self):
        portfolios = super().get_queryset().order_by('primeiro_nome')
        search = self.request.GET.get('search')
        if search:
            portfolios = portfolios.filter(primeiro_nome__icontains=search)
        return portfolios

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(self.request, 'portfolio_lista_parcial.html', context)  # Template parcial atualizado
        return super().render_to_response(context, **response_kwargs)

    # Função para gerenciar a navegação entre as páginas de portfólios
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        paginator = context['paginator']
        page_obj = paginator.get_page(page)
        context['portfolios'] = page_obj
        context['has_previous'] = page_obj.has_previous()
        context['has_next'] = page_obj.has_next()
        context['previous_page_number'] = page_obj.previous_page_number() if page_obj.has_previous() else None
        context['next_page_number'] = page_obj.next_page_number() if page_obj.has_next() else None
        return context

# ==============================================
# Detalhar os portfólios cadastrados
# ==============================================
class PortfolioDetailView(DetailView):
    model = Portfolio
    template_name = 'portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formacoes'] = Formacao.objects.filter(portfolio=self.object)
        context['experiencias_trabalho'] = ExperienciaTrabalho.objects.filter(portfolio=self.object)
        return context

    def get(self, request, *args, **kwargs):
        portfolio = self.get_object()
        if not request.user.is_superuser:
            return redirect(f'/{portfolio.primeiro_nome}-page/')
        return super().get(request, *args, **kwargs)


# ==============================================
# Cadastrar um novo portfólio
# ==============================================
@method_decorator(login_required(login_url='login'), name='dispatch')
class NewPortfolioCreateView(CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'new_portfolio.html'
    success_url = '/portfolios/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formacao_formset'] = FormacaoFormSet(self.request.POST)
            context['experiencia_formset'] = ExperienciaTrabalhoFormSet(self.request.POST)
        else:
            context['formacao_formset'] = FormacaoFormSet()
            context['experiencia_formset'] = ExperienciaTrabalhoFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formacao_formset = context['formacao_formset']
        experiencia_formset = context['experiencia_formset']

        if form.is_valid() and formacao_formset.is_valid() and experiencia_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()

            formacao_formset.instance = self.object
            experiencia_formset.instance = self.object
            formacao_formset.save()
            experiencia_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


# ==============================================
# Atualizar os portfólios cadastrados
# ==============================================
@method_decorator(login_required(login_url='login'), name='dispatch')
class PortfolioUpdateView(UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolio_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formacao_formset'] = FormacaoFormSet(self.request.POST, self.request.FILES, instance=self.object)
            context['experiencia_formset'] = ExperienciaTrabalhoFormSet(self.request.POST, self.request.FILES,
                                                                        instance=self.object)
        else:
            context['formacao_formset'] = FormacaoFormSet(instance=self.object)
            context['experiencia_formset'] = ExperienciaTrabalhoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formacao_formset = context['formacao_formset']
        experiencia_formset = context['experiencia_formset']

        # Verificar unicidade do email e telefone (exceto "não informado")
        email = form.cleaned_data.get('email')
        telefone = form.cleaned_data.get('telefone')

        if email != 'email@dominio.com' and Portfolio.objects.filter(
                Q(email=email) & ~Q(email="") & ~Q(pk=self.object.pk)).exists():
            form.add_error('email', 'Este email já está em uso.')
            return self.form_invalid(form)

        if telefone and telefone.lower() != "não informado" and Portfolio.objects.filter(telefone=telefone).exclude(
                pk=self.object.pk).exists():
            form.add_error('telefone', 'Este telefone já está em uso.')
            return self.form_invalid(form)

        if form.is_valid() and formacao_formset.is_valid() and experiencia_formset.is_valid():
            self.object = form.save()
            formacoes = formacao_formset.save(commit=False)
            for formacao in formacoes:
                formacao.portfolio = self.object
                formacao.save()
            for formacao in formacao_formset.deleted_objects:
                formacao.delete()

            experiencias = experiencia_formset.save(commit=False)
            for experiencia in experiencias:
                experiencia.portfolio = self.object
                experiencia.save()
            for experiencia in experiencia_formset.deleted_objects:
                experiencia.delete()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('portfolio_detail', kwargs={'pk': self.object.pk})


# ==============================================
# Apagar portfólios cadastrados
# ==============================================
@method_decorator(user_passes_test(admin_check, login_url='login'), name='dispatch')
class PortfolioDeleteView(DeleteView):
    model = Portfolio
    template_name = 'portfolio_delete.html'
    success_url = '/portfolios/'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        Formacao.objects.filter(portfolio=self.object).delete()
        ExperienciaTrabalho.objects.filter(portfolio=self.object).delete()
        return super().delete(request, *args, **kwargs)


# ==============================================
# Exibir a página personalizada do portfólio
# ==============================================
class PortfolioPageView(DetailView):
    model = Portfolio
    template_name = 'portfolio_page.html'
    context_object_name = 'portfolio'

    def get_object(self):
        primeiro_nome = self.kwargs.get('primeiro_nome')
        return Portfolio.objects.filter(primeiro_nome=primeiro_nome).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formacoes'] = Formacao.objects.filter(portfolio=self.object)
        context['experiencias_trabalho'] = ExperienciaTrabalho.objects.filter(portfolio=self.object)
        return context


# ==============================================
# Listar cursos cadastrados
# ==============================================
class CursosListView(ListView):
    model = Curso
    template_name = 'lista_cursos.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        instituicao_id = self.kwargs.get('instituicao_id')
        if instituicao_id:
            return Curso.objects.filter(instituicao_id=instituicao_id)
        return Curso.objects.all()


# ==============================================
# Detalhar os cursos cadastrados
# ==============================================
class CursoDetailView(DetailView):
    model = Curso
    template_name = 'curso_detail.html'
    context_object_name = 'curso'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instituicao'] = self.object.instituicao
        context['range_5'] = range(1, 6)  # Adiciona a lista de números de 1 a 5 ao contexto
        return context


# ==============================================
# Atualizar curso cadastrado (somente para superusuários)
# ==============================================
@method_decorator(user_passes_test(admin_check, login_url='login'), name='dispatch')
class CursoUpdateView(UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'curso_update.html'

    def get_success_url(self):
        return reverse_lazy('curso_detail', kwargs={'pk': self.object.pk})


# ==============================================
# Apagar curso cadastrado (somente para superusuários)
# ==============================================
@method_decorator(user_passes_test(admin_check, login_url='login'), name='dispatch')
class CursoDeleteView(DeleteView):
    model = Curso
    template_name = 'curso_delete.html'
    success_url = reverse_lazy('lista_cursos')


# ==============================================
# Listar instituições cadastradas
# ==============================================
class InstituicoesListView(ListView):
    model = Instituicao
    template_name = 'lista_instituicoes.html'
    context_object_name = 'instituicoes'

# ==============================================
# Cadastrar um novo curso (somente para superusuários)
# ==============================================
@method_decorator(user_passes_test(admin_check, login_url='login'), name='dispatch')
class CadastroCursoView(CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'cadastro_curso.html'
    success_url = reverse_lazy('lista_cursos')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.instituicao.atualizar_quantidade_cursos()
        return response


# ==============================================
# Gerar PDF do cartão de portfólio
# ==============================================
def render_pdf_view(request, pk):
    try:
        # Buscando o portfólio e os dados relacionados
        portfolio = get_object_or_404(Portfolio, pk=pk)
        formacoes = Formacao.objects.filter(portfolio=portfolio)
        experiencias_trabalho = ExperienciaTrabalho.objects.filter(portfolio=portfolio)

        # Novo template simplificado para o cartão do PDF
        template_path = 'pdfPortfolio.html'
        context = {
            'portfolio': portfolio,
            'formacoes': formacoes,
            'experiencias_trabalho': experiencias_trabalho,
        }

        # Configurando a resposta do PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{portfolio.primeiro_nome}_cartao.pdf"'

        # Renderizando o HTML e criando o PDF
        template = get_template(template_path)
        html = template.render(context)

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Erro ao gerar PDF: {}'.format(pisa_status.err), status=400)

        # Retornando o PDF gerado
        return response

    except Exception as e:
        return HttpResponse('Erro ao processar a solicitação: {}'.format(str(e)), status=500)
