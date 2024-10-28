from django.contrib import admin
from portfolio.models import Portfolio, Formacao, ExperienciaTrabalho


class FormacaoInline(admin.TabularInline):
    """
    Criação de um inline para associar Formacao ao Portfolio.
    Assim, é possível adicionar ou editar formações diretamente na página de edição do Portfolio.
    """
    model = Formacao
    extra = 1
    can_delete = True


class ExperienciaTrabalhoInline(admin.TabularInline):
    """
    Criação de um inline para associar ExperienciaTrabalho ao Portfolio.
    Assim, é possível adicionar ou editar experiências de trabalho diretamente na página de edição do Portfolio.
    """
    model = ExperienciaTrabalho
    extra = 1
    can_delete = True


class PortfolioAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista de portfólios no painel do admin
    list_display = (
        'primeiro_nome', 'sobrenome', 'principal_formacao', 'tempo_experiencia', 'numero_projetos', 'numero_companhias'
    )

    # Campos que podem ser usados na barra de pesquisa
    search_fields = ('primeiro_nome', 'sobrenome', 'principal_formacao')

    # Filtros que aparecerão na barra lateral
    list_filter = ('principal_formacao', 'tempo_experiencia')

    # Adicionando as inlines para permitir edição de Formacao e ExperienciaTrabalho diretamente no Portfolio
    inlines = [FormacaoInline, ExperienciaTrabalhoInline]


class FormacaoAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista de formações no painel do admin
    list_display = ('portfolio', 'nome_instituicao', 'curso', 'data_conclusao')

    # Campos que podem ser usados na barra de pesquisa
    search_fields = ('portfolio__primeiro_nome', 'nome_instituicao', 'curso')

    # Filtros que aparecerão na barra lateral
    list_filter = ('nome_instituicao', 'curso')


class ExperienciaTrabalhoAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista de experiências de trabalho no painel do admin
    list_display = ('portfolio', 'nome_empresa', 'cargo', 'data_inicio', 'data_fim')

    # Campos que podem ser usados na barra de pesquisa
    search_fields = ('portfolio__primeiro_nome', 'nome_empresa', 'cargo')

    # Filtros que aparecerão na barra lateral
    list_filter = ('nome_empresa', 'cargo')


# Registro dos modelos no painel do admin
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Formacao, FormacaoAdmin)
admin.site.register(ExperienciaTrabalho, ExperienciaTrabalhoAdmin)
