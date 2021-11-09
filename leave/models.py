from django.contrib.auth.models import AbstractUser
from django.db import models
import decimal
import datetime

# username: superuser password:superuser

"""
default argument: default value for the field
null vs blank argument: null is purely database-related, whereas blank is validation-related
If a field has blank=True, form validation will allow entry of an empty value. If a field has blank=False, the field will be required.
if field is optional, put null=True to allow that in database. put blank=True to allow in form
"""
DEFAULT_LEAVES = decimal.Decimal("14")
PENDING_STATUS = "pending"
APPROVED_STATUS = "approved"
REJECTED_STATUS = "rejected"

# Create your models here.
class User(AbstractUser):
    pass

class Employee(models.Model):
    employee = models.ForeignKey("User", on_delete=models.CASCADE)
    # employee = 1, manager = 2
    hierarchy = models.IntegerField()
    superior = models.ManyToManyField("User", related_name="subordinates")

    leave_count = models.DecimalField(default=DEFAULT_LEAVES, max_digits=3, decimal_places=1)

    def name(self):
        return self.employee.username

    def __str__(self) -> str:
        return f"{self.employee.username} is a {'employee' if self.hierarchy == 1 else 'manager'}"

class Leave(models.Model):
    employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="leaves")
    
    start: datetime.datetime = models.DateTimeField()
    end: datetime.datetime = models.DateTimeField()

    # pending, approved, rejected
    status = models.CharField(max_length=100, default=PENDING_STATUS)

    def num_days_taken(self):
        """Returns number of days taken"""
        return (self.end - self.start) / datetime.timedelta(days=1)

    def serialize(self):
        """Return dict for manager main page"""
        return {
            "id": self.id,
            "employee": self.employee.name(),
            "start": self.start.strftime('%Y-%m-%d') + " " + ("AM" if self.start.hour==0 else "PM"),
            "end": (self.end -  datetime.timedelta(hours=12)).strftime('%Y-%m-%d') + " " + ("PM" if self.end.hour==0 else "AM"),
            "duration": self.num_days_taken(),
            "approved": self.status
        } 

    def __str__(self) -> str:
        return f"{self.employee.employee.username} is taking leave from {self.start.strftime('%Y-%m-%d %H')} to {self.end.strftime('%Y-%m-%d %H')}. {self.status}"
