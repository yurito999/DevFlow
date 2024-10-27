from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView
from portfolio.views import (
    PortfolioListView, NewPortfolioCreateView, PortfolioDetailView, PortfolioUpdateView,
    PortfolioDeleteView, PortfolioPageView, search_profiles, CursosListView, InstituicoesListView,
    CadastroCursoView, CursoDetailView, CursoUpdateView, CursoDeleteView, render_pdf_view
)
from accounts.views import register_view, login_view, logout_view

# Função para verificar se o usuário é superusuário
admin_required = user_passes_test(lambda u: u.is_superuser)

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # Redireciona a URL raiz para a página de lista de portfólios
    path('', lambda request: redirect('portfolio_list'), name='home'),

    # URLs para o app Portfolio
    path('portfolios/', PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolios/page/', PortfolioListView.as_view(), name='portfolio_list_partial'),  # Novo endpoint para AJAX
    path('portfolio/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('<str:primeiro_nome>-page/', PortfolioPageView.as_view(), name='portfolio_page'),

    # URLs protegidas para criação, atualização e exclusão de portfólios
    path('portfolio/<int:pk>/update/', login_required(PortfolioUpdateView.as_view()), name='update'),
    path('portfolio/<int:pk>/delete/', login_required(PortfolioDeleteView.as_view()), name='delete'),
    path('new_portfolio/', login_required(NewPortfolioCreateView.as_view()), name='new_portfolio'),

    # URL para busca de portfólios
    path('search-profiles/', search_profiles, name='search_profiles'),

    # URLs para autenticação de usuários
    path('login/', login_view, name='login'),
    path('logout/', login_required(logout_view), name='logout'),
    path('register/', admin_required(register_view), name='register'),

    # URLs para Cursos e Instituições
    path('cursos/', CursosListView.as_view(), name='lista_cursos'),
    path('curso/<int:pk>/', CursoDetailView.as_view(), name='curso_detail'),
    path('curso/<int:pk>/update/', admin_required(CursoUpdateView.as_view()), name='update_curso'),
    path('curso/<int:pk>/delete/', admin_required(CursoDeleteView.as_view()), name='delete_curso'),
    path('instituicoes/', InstituicoesListView.as_view(), name='institutions_list'),

    # URL protegida para cadastrar curso (apenas superusuários)
    path('cadastrar-curso/', admin_required(CadastroCursoView.as_view()), name='cadastro_curso'),

    # URL para a página "Sobre"
    path('sobre/', TemplateView.as_view(template_name="sobre.html"), name='sobre'),
    path('expo/', TemplateView.as_view(template_name="expo.html"), name='expo'),

    # URL para gerar o PDF do cartão de portfólio
    path('portfolio/<int:pk>/pdf/', render_pdf_view, name='portfolio_pdf'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
