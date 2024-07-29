from django.shortcuts import render, redirect
from .models import User, Expense, Split
from .forms import UserForm, ExpenseForm, SplitForm
from django.http import HttpResponse
from django.contrib import messages

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.filter(email=email).first()
        if user:
            request.session['user_id'] = user.id
            return redirect('split_expense')
        else:
            return render(request, 'login.html', {'error': 'Invalid email'})
    return render(request, 'login.html')

def split_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            split_type = form.cleaned_data['split_type']
            user_ids = request.POST.getlist('users')
            users = User.objects.filter(id__in=user_ids)  # Filter users based on selected IDs

            if not users:
                messages.error(request, 'No users selected.')
                return redirect('split_expense')

            if split_type == 'equal':
                if len(users) == 0:
                    messages.error(request, 'No users selected.')
                    return redirect('split_expense')
                
                split_amount = amount / len(users)
                for user in users:
                    Split.objects.create(user=user, amount=split_amount, description=description, split_type=split_type)
                
                messages.success(request, f'Equal split: Each user owes {split_amount}')
                return redirect('split_expense')
                
            elif split_type == 'exact':
                exact_amounts = [float(request.POST.get(f'exact_amounts_{user.id}', 0)) for user in users]
                if len(exact_amounts) != len(users):
                    messages.error(request, 'The number of exact amounts does not match the number of selected users.')
                    return redirect('split_expense')
                
                total_amount = sum(exact_amounts)
                if total_amount != amount:
                    messages.error(request, 'The sum of exact amounts does not match the total amount.')
                    return redirect('split_expense')
                
                for user, exact_amount in zip(users, exact_amounts):
                    Split.objects.create(user=user, amount=exact_amount, description=description, split_type=split_type)
                
                messages.success(request, f'Exact split: {exact_amounts}')
                return redirect('split_expense')
                
            elif split_type == 'percentage':
                percentages = [float(request.POST.get(f'percentages_{user.id}', 0)) for user in users]
                if len(percentages) != len(users):
                    messages.error(request, 'The number of percentages does not match the number of selected users.')
                    return redirect('split_expense')
                
                total_percentage = sum(percentages)
                if total_percentage != 100:
                    messages.error(request, 'The sum of percentages must be 100%.')
                    return redirect('split_expense')
                
                for user, percentage in zip(users, percentages):
                    split_amount = (amount * percentage) / 100
                    Split.objects.create(user=user, amount=split_amount, description=description, split_type=split_type)
                
                messages.success(request, f'Percentage split: {percentages}')
                return redirect('split_expense')
    else:
        form = ExpenseForm()
    
    users = User.objects.all()
    return render(request, 'split_expense.html', {'form': form, 'users': users})


