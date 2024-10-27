from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


# ==============================================
# View para registro de superusuário
# ==============================================
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Validação de senhas
        if password1 != password2:
            messages.error(request, 'As senhas não coincidem.')
        else:
            # Verificação se o usuário ou email já existe
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Usuário já existe.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email já cadastrado.')
            else:
                # Criação de superusuário
                user = User.objects.create_superuser(username=username, email=email, password=password1)
                user.save()
                messages.success(request, 'Superusuário criado com sucesso.')
                return redirect('login')

    return render(request, 'register.html', {})


# ==============================================
# View para login de usuário
# ==============================================
def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]

        # Autenticação do usuário
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('portfolio_list')  # Redireciona para a lista de portfólios após login bem-sucedido
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    login_form = AuthenticationForm()
    return render(request, 'login.html', {'login_form': login_form})


# ==============================================
# View para logout de usuário
# ==============================================
def logout_view(request):
    # Realiza o logout do usuário atual
    logout(request)
    messages.info(request, 'Você saiu da sua conta com sucesso.')
    return redirect('login')  # Redireciona para a página de login após o logout
