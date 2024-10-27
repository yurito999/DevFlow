from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Instituicao(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    endereco = models.TextField()
    quantidade_cursos = models.PositiveIntegerField(default=0, editable=False)
    quantidade_alunos = models.PositiveIntegerField(default=0, editable=False)
    imagem = models.ImageField(upload_to='instituicao_imagens/', blank=True, null=True)  # Campo para imagem da instituição

    def atualizar_quantidade_cursos(self):
        """
        Atualiza o campo quantidade_cursos com base nos cursos relacionados.
        """
        self.quantidade_cursos = self.cursos_list.count()
        self.save(update_fields=['quantidade_cursos'])

    def atualizar_quantidade_alunos(self):
        """
        Atualiza o campo quantidade_alunos com base nos alunos dos cursos relacionados.
        """
        self.quantidade_alunos = sum(curso.nota_mec for curso in self.cursos_list.all())
        self.save(update_fields=['quantidade_alunos'])

    def __str__(self):
        return self.nome


class Curso(models.Model):
    nome = models.CharField(max_length=255)
    sala = models.CharField(max_length=50)
    periodo = models.CharField(max_length=100)
    nota_mec = models.PositiveIntegerField(default=0)
    instituicao = models.ForeignKey(Instituicao, related_name='cursos_list', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='curso_imagens/', blank=True, null=True)  # Campo para imagem do curso
    coordenador = models.CharField(max_length=255, blank=True, null=True)
    turnos = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para atualizar a quantidade de alunos na instituição associada.
        """
        super().save(*args, **kwargs)
        self.instituicao.atualizar_quantidade_alunos()
        self.instituicao.atualizar_quantidade_cursos()

    def __str__(self):
        return f"{self.nome} - {self.instituicao.nome}"


class Portfolio(models.Model):
    # Campos de identificação e atuação
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Permite nulo até que um usuário seja associado
    primeiro_nome = models.CharField(max_length=100, blank=True, null=True)
    sobrenome = models.CharField(max_length=100, blank=True, null=True)
    principal_formacao = models.CharField(max_length=200, blank=True, null=True)

    # Curso, período, sala e instituição
    curso = models.ForeignKey(Curso, related_name='portfolios_list', on_delete=models.SET_NULL, null=True, blank=True)
    instituicao = models.ForeignKey(Instituicao, related_name='portfolios_list', on_delete=models.SET_NULL, null=True, blank=True)
    periodo = models.CharField(max_length=100, blank=True, null=True)
    sala = models.CharField(max_length=50, blank=True, null=True)

    # Descrições com valores padrão
    resumo = models.TextField(default="Resumo não informado", blank=True, null=True)
    sobre = models.TextField(default="Informações não fornecidas", blank=True, null=True)

    # Detalhes de experiência com validação
    tempo_experiencia = models.PositiveIntegerField(default=1, help_text="Tempo de experiência em anos")
    numero_projetos = models.PositiveIntegerField(default=1, help_text="Número de projetos concluídos")
    numero_companhias = models.PositiveIntegerField(default=0, editable=False)  # Calculado automaticamente

    # Especialidades
    especialidades = models.TextField(default="Nenhum serviço informado", blank=True, null=True)

    # Informações de contato com valores padrão
    telefone = models.CharField(max_length=20, default="Não informado", blank=True, null=True)
    email = models.EmailField(default="email@dominio.com", blank=True, null=True)
    localidade = models.CharField(max_length=100, default="Localidade não informada", blank=True, null=True)

    # Foto do perfil (opcional)
    photo = models.ImageField(upload_to='portfolio_photos/', blank=True, null=True)

    # Redes sociais (opcionais)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    dribbble = models.URLField(blank=True, null=True)

    def clean(self):
        # Valida que o número de anos de experiência e o número de projetos são coerentes
        if self.tempo_experiencia < 1:
            raise ValidationError('O tempo de experiência deve ser pelo menos 1 ano.')
        if self.numero_projetos < 1:
            raise ValidationError('O número de projetos deve ser pelo menos 1.')

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para atualizar o campo 'numero_companhias' automaticamente com base nas experiências.
        Garante também que os dados do portfólio são salvos corretamente.
        """
        super().save(*args, **kwargs)  # Primeiro salva o portfólio para garantir que há um ID
        self.numero_companhias = self.experiencias_list.count()  # Atualiza o número de companhias com base nas experiências
        super().save(update_fields=['numero_companhias'])  # Salva novamente apenas o campo atualizado

    def __str__(self):
        return f"{self.primeiro_nome} {self.sobrenome}" if self.primeiro_nome and self.sobrenome else "Portfólio sem nome completo"


class Formacao(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='formacoes_list', on_delete=models.CASCADE)
    nome_instituicao = models.CharField(max_length=255, blank=True, null=True)
    curso = models.CharField(max_length=255)
    data_conclusao = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.curso} - {self.nome_instituicao if self.nome_instituicao else 'Instituição não informada'}"


class ExperienciaTrabalho(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='experiencias_list', on_delete=models.CASCADE)
    nome_empresa = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)  # Permitir nulo para experiências ainda em andamento

    def __str__(self):
        if self.data_fim:
            return f"{self.cargo} - {self.nome_empresa} ({self.data_inicio} - {self.data_fim})"
        else:
            return f"{self.cargo} - {self.nome_empresa} ({self.data_inicio} - Atualmente)"

    def clean(self):
        # Valida que a data de fim, se fornecida, é posterior à data de início
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValidationError('A data de fim não pode ser anterior à data de início.')