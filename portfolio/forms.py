from django import forms
from portfolio.models import Portfolio, Formacao, ExperienciaTrabalho, Curso
import re
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = '__all__'
        widgets = {
            'primeiro_nome': forms.TextInput(attrs={'placeholder': 'Primeiro Nome', 'class': 'form-control'}),
            'sobrenome': forms.TextInput(attrs={'placeholder': 'Sobrenome', 'class': 'form-control'}),
            'principal_formacao': forms.TextInput(attrs={'placeholder': 'Principal Formação', 'class': 'form-control'}),
            'resumo': forms.Textarea(attrs={'placeholder': 'Resumo', 'class': 'form-control'}),
            'sobre': forms.Textarea(attrs={'placeholder': 'Sobre', 'class': 'form-control'}),
            'tempo_experiencia': forms.NumberInput(attrs={'placeholder': 'Tempo de Experiência (anos)', 'class': 'form-control'}),
            'numero_projetos': forms.NumberInput(attrs={'placeholder': 'Número de Projetos', 'class': 'form-control'}),
            'especialidades': forms.Textarea(attrs={'placeholder': 'Especialidades', 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'placeholder': 'Telefone', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
            'localidade': forms.TextInput(attrs={'placeholder': 'Localidade', 'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'placeholder': 'LinkedIn (Opcional)', 'class': 'form-control'}),
            'github': forms.URLInput(attrs={'placeholder': 'GitHub (Opcional)', 'class': 'form-control'}),
            'dribbble': forms.URLInput(attrs={'placeholder': 'Dribbble (Opcional)', 'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    # Validação para o campo 'telefone'
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')

        # Se o campo estiver vazio, retornar 'não informado'
        if not telefone:
            telefone = 'Não informado'

        # Verificação de duplicidade, ignorando instâncias com 'não informado'
        if telefone != 'Não informado' and Portfolio.objects.filter(telefone=telefone).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este número de telefone já está em uso.')

        return telefone

    # Validação para o campo 'email'
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_padrao = 'email@dominio.com'
        if not email or email == email_padrao:
            email = email_padrao

        # Verificação de duplicidade, ignorando instâncias com email padrão
        if email != email_padrao and Portfolio.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este email já está em uso.')
        return email

    # Validação para LinkedIn
    def clean_linkedin(self):
        linkedin = self.cleaned_data.get('linkedin')
        if linkedin:
            if not re.match(r'^https?://(www\.)?linkedin\.com/in/.+', linkedin):
                raise ValidationError('Insira um perfil LinkedIn válido.')
            if Portfolio.objects.filter(linkedin=linkedin).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este perfil LinkedIn já está em uso.')
        return linkedin

    # Validação para GitHub
    def clean_github(self):
        github = self.cleaned_data.get('github')
        if github:
            if not re.match(r'^https?://(www\.)?github\.com/.+', github):
                raise ValidationError('Insira um perfil GitHub válido.')
            if Portfolio.objects.filter(github=github).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este perfil GitHub já está em uso.')
        return github

# Criar formsets para Formacao e ExperienciaTrabalho
FormacaoFormSet = inlineformset_factory(
    Portfolio, Formacao,
    fields=['nome_instituicao', 'curso', 'data_conclusao'],
    extra=1,
    can_delete=True,  # Permite deletar as formações existentes
    widgets={
        'nome_instituicao': forms.TextInput(attrs={'placeholder': 'Nome da Instituição', 'class': 'form-control'}),
        'curso': forms.TextInput(attrs={'placeholder': 'Curso', 'class': 'form-control'}),
        'data_conclusao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    }
)

ExperienciaTrabalhoFormSet = inlineformset_factory(
    Portfolio, ExperienciaTrabalho,
    fields=['nome_empresa', 'cargo', 'data_inicio', 'data_fim'],
    extra=1,
    can_delete=True,  # Permite deletar as experiências existentes
    widgets={
        'nome_empresa': forms.TextInput(attrs={'placeholder': 'Nome da Empresa', 'class': 'form-control'}),
        'cargo': forms.TextInput(attrs={'placeholder': 'Cargo', 'class': 'form-control'}),
        'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    }
)

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do Curso', 'class': 'form-control'}),
            'sala': forms.TextInput(attrs={'placeholder': 'Sala', 'class': 'form-control'}),
            'periodo': forms.TextInput(attrs={'placeholder': 'Período', 'class': 'form-control'}),
            'coordenador': forms.TextInput(attrs={'placeholder': 'Coordenador', 'class': 'form-control'}),
            'turnos': forms.TextInput(attrs={'placeholder': 'Turnos', 'class': 'form-control'}),
            'numero_alunos': forms.NumberInput(attrs={'placeholder': 'Número de Alunos', 'class': 'form-control'}),
            'instituicao': forms.Select(attrs={'class': 'form-control'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
