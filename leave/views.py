import datetime
import json 
from typing import Optional
import decimal

from django.contrib.auth import authenticate, login, logout
from django.db.utils import IntegrityError
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.http.request import HttpRequest
from django.urls.base import reverse
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.views.decorators.csrf import csrf_exempt

from .models import Employee, Leave, User

MANAGER = 2
EMPLOYEE = 1
PENDING_STATUS = "pending"
APPROVED_STATUS = "approved"
REJECTED_STATUS = "rejected"

# Create your views here.
@login_required(login_url="login")
def index(request: HttpRequest):
    """Shows the dashboard like view"""
    current_employee: Employee = Employee.objects.get(employee=request.user)
    if current_employee.hierarchy == MANAGER:
        context = manager_index_context(current_employee)
    else: 
        # context for employees
        context = employee_index_context(current_employee)

    return render(request=request, template_name="leave/index.html", context=context)

def employee_index_context(current_employee: Employee):
    """Returns the context for displaying employee main page"""
    return {
        "is_manager": current_employee.hierarchy == MANAGER,
        "leave_count": current_employee.leave_count,
        "superior_list": current_employee.superior.all()
    }

def manager_index_context(current_employee: Employee):
    """Returns the context for displaying manager main page"""
    employee_list: QuerySet = current_employee.employee.subordinates.all()

    all_employees = [employee.name() for employee in Employee.objects.filter(hierarchy__exact=EMPLOYEE) if employee not in employee_list]
    approved = [leave.serialize() for employee in employee_list for leave in employee.leaves.all().filter(status__exact=APPROVED_STATUS)]
    pending = [leave.serialize() for employee in employee_list for leave in employee.leaves.all().filter(status__exact=PENDING_STATUS)]
    
    return {
        "is_manager": current_employee.hierarchy == MANAGER,
        "all_employees": all_employees,
        "employee_list": employee_list,
        "approved_leaves": approved,
        "pending_leaves": pending
    }

@login_required(login_url="login")
def apply_leave(request: HttpRequest):
    """
    Processes information from apply leave form 
    startDate, startTime, endDate, endTime, superior
    """
    employee: Employee = Employee.objects.get(employee=request.user)

    startDate = [int(i) for i in request.POST['startDate'].split(sep="-")]
    startTime = 0 if request.POST['startTime'] == "AM" else 12
    endDate = [int(i) for i in request.POST['endDate'].split(sep="-")]
    endTime = 0 if request.POST['endTime'] == "AM" else 12

    # create datetime object (received a naive datetime)
    start = datetime.datetime(*startDate, startTime)
    end = datetime.datetime(*endDate, endTime) + datetime.timedelta(hours=12)

    # create superior object 
    try:
        superior = Employee.objects.get(employee=User.objects.get(username=request.POST['superior']))
    except User.DoesNotExist:
        superior = None      
    print(start, end, superior)

    # if existing leave, dont create new leave
    try:
        existing_leave: Leave = Leave.objects.get(employee=employee, start=start, end=end) 
    except Leave.DoesNotExist:
        # create leave entry 
        new_leave = Leave(employee=employee, start=start, end=end)
        new_leave.save()

    return HttpResponseRedirect(reverse(viewname="index"))

@csrf_exempt
@login_required(login_url="login")
def approve_reject_leave(request: HttpRequest):
    """Updates database when manager approves or rejects leave"""
    if request.method == "PUT":
        data: dict = json.loads(request.body)
        print(data)
        leave: Leave = Leave.objects.get(pk=data['leave_id'])

        if data['action'] == "approve":
            status = APPROVED_STATUS 
            # updates database
            leave.status = status
            leave.save()

            # update leave count of employee if approved
            leave.employee.leave_count -= decimal.Decimal(leave.num_days_taken())
            print(leave.employee.leave_count)
            leave.employee.save()
        elif data['action'] == "reject":
            status = REJECTED_STATUS 
            # updates database
            leave.status = status
            leave.save()

        return JsonResponse({"success": True}) 
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)

def approved_leaves_list(request: HttpRequest):
    """Return JSON of approved leaves"""
    if request.method == "GET":
        current_employee: Employee = Employee.objects.get(employee=request.user)
        employee_list: QuerySet = current_employee.employee.subordinates.all()
        approved = [leave.serialize() for employee in employee_list for leave in employee.leaves.all().filter(status__exact=APPROVED_STATUS)]
        print(approved)
        return JsonResponse(approved, safe=False) 
    else:
        return JsonResponse({"error": "GET request required."}, status=400) 

@csrf_exempt
@login_required(login_url="login")
def add_employee_to_superior(request: HttpRequest):
    """Allows superior to add employee"""
    if request.method == "PUT":
        data: dict = json.loads(request.body)
        print(request.user, data)

        # add employee to superior 
        try:
            new_employee: Employee = Employee.objects.get(employee=User.objects.get(username=data['employee']))
        except User.DoesNotExist:
            return JsonResponse({"success": False})
        new_employee.superior.add(request.user)
        new_employee.save()
        
        return JsonResponse({"success": True}) 
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)

def login_view(request: HttpRequest):
    """Displays login page"""
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user: Optional[User] = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "leave/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "leave/login.html")

def logout_view(request: HttpRequest):
    """View for users to logout"""
    logout(request)
    return HttpResponseRedirect(reverse("index")) 

def register(request: HttpRequest):
    """Register for a new account"""
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        is_manager = request.POST.get('is_manager', False)
        
        if password != confirmation:
            return render(request=request, template_name="leave/register.html", context={
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user: User = User.objects.create_user(username, email, password)
            Employee(employee=user, hierarchy=2 if is_manager else 1).save()
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "leave/register.html", {
                "message": "Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "leave/register.html")

