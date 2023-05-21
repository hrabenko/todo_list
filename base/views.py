from collections import defaultdict
from .models import Task, Category
from .forms import TaskForm
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from reportlab.pdfgen import canvas
from django.http import HttpResponse

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

class TaskList(LoginRequiredMixin,ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_tasks = Task.objects.filter(user=user)
        context['tasks'] = user_tasks

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = user_tasks.filter(title__icontains=search_input)

        context['search_input'] = search_input

        priority_id = self.request.GET.get('priority')
        if priority_id:
            context['tasks'] = user_tasks.filter(priority=priority_id)

        category_id = self.request.GET.get('task_category')
        if category_id:
            context['tasks'] = user_tasks.filter(task_category=category_id)

        complete_id = self.request.GET.get('complete')
        if complete_id:
            context['tasks'] = user_tasks.filter(complete=complete_id)
        sorting_id =self.request.GET.get('sorting')
        if sorting_id == "1":
            context['tasks'] = user_tasks.order_by('priority')
        if sorting_id == "2":
            context['tasks'] = user_tasks.order_by('deadline')
        if sorting_id == "3":
            context['tasks'] = user_tasks.order_by('-priority')
        if sorting_id == "4":
            context['tasks'] = user_tasks.order_by('-deadline')

        categories = Category.objects.filter(user=user)
        context['categories'] = categories

        # Calculate overall completion percentage
        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(complete=True).count()
        if total_tasks > 0:
            overall_completion_percentage = (completed_tasks / total_tasks) * 100
        else:
            overall_completion_percentage = 0

        context['overall_completion_percentage'] = overall_completion_percentage

        return context

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class ExportPDFView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'base/pdf_template.html'

    def render_to_response(self, context, **response_kwargs):
        user = self.request.user
        tasks = context['object_list'].filter(user=user)

        # Filter out tasks without a category
        tasks_with_category = tasks.exclude(task_category__isnull=True)

        # Group tasks by category
        task_dict = defaultdict(list)
        task_dict['Without Category'] = []  # Placeholder for tasks without category
        for task in tasks_with_category:
            task_dict[task.task_category.name].append(task)

        # Add tasks without category
        tasks_without_category = tasks.filter(task_category__isnull=True)
        task_dict['Without Category'].extend(tasks_without_category)

        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="todo_list.pdf"'
        p = canvas.Canvas(response)

        # Generate PDF content
        p.setFont('Helvetica-Bold', 16)
        p.drawString(100, 800, 'Tasks:')

        p.setFont('Helvetica', 12)
        y = 770
        for category, tasks in task_dict.items():
            p.drawString(100, y, category)
            y -= 20
            for task in tasks:
                status = "Done" if task.complete else "Not Done"
                task_line = f"{task.title} - {status}"
                p.drawString(120, y, task_line)
                y -= 20
            y -= 10  # Additional spacing between categories

        p.showPage()
        p.save()

        return response

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('tasks')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('tasks')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

class CategoryDetail(LoginRequiredMixin, DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'base/category.html'

class CategoryCreate(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name', 'description']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CategoryCreate, self).form_valid(form)
    
class CategoryUpdate(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name', 'description']
    success_url = reverse_lazy('tasks')

class CategoryDelete(LoginRequiredMixin, DeleteView):
    model = Category
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')