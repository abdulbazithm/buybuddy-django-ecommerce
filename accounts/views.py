from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm
from .models import Address
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '🎉 Account created successfully! You can now log in.')
            return redirect('login')
        else:
            # Show detailed form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}! 🎉')
            return redirect('home')  # Redirect to homepage after login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def add_address(request):
    if request.method == "POST":
        has_default = Address.objects.filter(user=request.user, is_default=True).exists()

        address = Address.objects.create(
            user=request.user,
            full_name=request.POST["full_name"],
            phone=request.POST["phone"],
            address_line=request.POST["address_line"],
            city=request.POST["city"],
            state=request.POST["state"],
            country=request.POST["country"],
            postal_code=request.POST["postal_code"],
            is_default=False
        )

        if not has_default:
            address.is_default = True
            address.save()

        messages.success(request, "Address added successfully!")

        next_url = request.GET.get("next", "address_list")
        return redirect(next_url)

    return render(request, "accounts/add_address.html")

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user).order_by('-is_default')
    return render(request, "accounts/address_list.html", {"addresses": addresses})


@login_required
def edit_address(request, id):
    address = Address.objects.get(id=id, user=request.user)

    if request.method == "POST":
        address.full_name = request.POST["full_name"]
        address.phone = request.POST["phone"]
        address.address_line = request.POST["address_line"]
        address.city = request.POST["city"]
        address.state = request.POST["state"]
        address.country = request.POST["country"]
        address.postal_code = request.POST["postal_code"]
        address.save()

        messages.success(request, "Address updated successfully! 🎉")
        return redirect("address_list")

    return render(request, "accounts/edit_address.html", {"address": address})

@login_required
def delete_address(request, id):
    address = Address.objects.get(id=id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully! 🗑️")
    return redirect("address_list")


@login_required
def set_default_address(request, id):
    Address.objects.filter(user=request.user).update(is_default=False)
    address = Address.objects.get(id=id, user=request.user)
    address.is_default = True
    address.save()

    messages.success(request, "Default address updated ✔️")
    return redirect("address_list")

@login_required
def profile_view(request):
    # Fetch saved addresses for logged-in user
    addresses = Address.objects.filter(user=request.user)

    return render(request, 'accounts/profile.html', {
        'addresses': addresses
    })