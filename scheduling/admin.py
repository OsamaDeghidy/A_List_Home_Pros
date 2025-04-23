from django.contrib import admin
from .models import AvailabilitySlot, UnavailableDate, Appointment, AppointmentNote


class AppointmentNoteInline(admin.TabularInline):
    model = AppointmentNote
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'contractor', 'get_day_name', 'start_time', 'end_time', 'is_recurring']
    list_filter = ['day_of_week', 'is_recurring', 'contractor']
    search_fields = ['contractor__business_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_day_name(self, obj):
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return day_names[obj.day_of_week]
    get_day_name.short_description = 'Day'


@admin.register(UnavailableDate)
class UnavailableDateAdmin(admin.ModelAdmin):
    list_display = ['id', 'contractor', 'date', 'reason']
    list_filter = ['date', 'contractor']
    search_fields = ['contractor__business_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'contractor', 'appointment_date', 'start_time', 'end_time', 'status']
    list_filter = ['status', 'appointment_date', 'contractor']
    search_fields = ['client__name', 'contractor__business_name', 'location', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AppointmentNoteInline]
    list_editable = ['status']


@admin.register(AppointmentNote)
class AppointmentNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment', 'user', 'note_preview', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at', 'user']
    search_fields = ['note', 'user__name', 'appointment__client__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note Preview'
