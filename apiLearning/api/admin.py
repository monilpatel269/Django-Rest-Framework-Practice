from django.contrib import admin
from api.models import Student, Subject, Teacher, User

# Register your models here.
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name','created_on']


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(User)