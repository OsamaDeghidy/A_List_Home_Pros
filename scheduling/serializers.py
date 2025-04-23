from rest_framework import serializers
from django.contrib.auth import get_user_model
from contractors.models import ContractorProfile, ServiceCategory
from contractors.serializers import ServiceCategorySerializer, ContractorProfileSerializer
from users.serializers import UserSerializer
from .models import AvailabilitySlot, UnavailableDate, Appointment, AppointmentNote

User = get_user_model()


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """Serializer for contractor availability slots"""
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AvailabilitySlot
        fields = ['id', 'contractor', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_recurring']
        read_only_fields = ['id']
    
    def get_day_name(self, obj):
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return day_names[obj.day_of_week]


class UnavailableDateSerializer(serializers.ModelSerializer):
    """Serializer for contractor unavailable dates"""
    class Meta:
        model = UnavailableDate
        fields = ['id', 'contractor', 'date', 'reason']
        read_only_fields = ['id']


class AppointmentNoteSerializer(serializers.ModelSerializer):
    """Serializer for appointment notes"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AppointmentNote
        fields = ['id', 'appointment', 'user', 'note', 'is_private', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']
    
    def create(self, validated_data):
        """Create a new appointment note with the current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments"""
    client = UserSerializer(read_only=True)
    contractor = ContractorProfileSerializer(read_only=True)
    service_category = ServiceCategorySerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notes = AppointmentNoteSerializer(source='appointment_notes', many=True, read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'contractor', 'service_category', 'appointment_date', 
            'start_time', 'end_time', 'status', 'status_display', 'notes', 
            'location', 'estimated_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    class Meta:
        model = Appointment
        fields = [
            'contractor', 'service_category', 'appointment_date', 
            'start_time', 'end_time', 'notes', 'location', 'estimated_cost'
        ]
    
    def validate(self, data):
        """
        Validate that the appointment time is available for the contractor
        and that the contractor offers the selected service
        """
        contractor = data['contractor']
        appointment_date = data['appointment_date']
        start_time = data['start_time']
        end_time = data['end_time']
        service_category = data.get('service_category')
        
        # Check if contractor offers this service
        if service_category and not contractor.service_categories.filter(id=service_category.id).exists():
            raise serializers.ValidationError(
                f"This contractor does not offer {service_category.name} services"
            )
        
        # Check if the contractor is available on this date
        if UnavailableDate.objects.filter(contractor=contractor, date=appointment_date).exists():
            raise serializers.ValidationError("The contractor is not available on this date")
        
        # Check if the time slot falls within the contractor's availability
        day_of_week = appointment_date.weekday()
        available_slots = AvailabilitySlot.objects.filter(
            contractor=contractor,
            day_of_week=day_of_week,
            start_time__lte=start_time,
            end_time__gte=end_time
        )
        
        if not available_slots.exists():
            raise serializers.ValidationError("The contractor is not available during this time slot")
        
        # Check for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            contractor=contractor,
            appointment_date=appointment_date,
            status__in=['REQUESTED', 'CONFIRMED'],
        ).filter(
            # Check for time overlap
            models.Q(start_time__lt=end_time, end_time__gt=start_time)
        )
        
        if overlapping_appointments.exists():
            raise serializers.ValidationError("The contractor already has an appointment during this time")
        
        return data
    
    def create(self, validated_data):
        """Create a new appointment with the current user as client"""
        validated_data['client'] = self.context['request'].user
        validated_data['status'] = 'REQUESTED'
        return super().create(validated_data)


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointments"""
    class Meta:
        model = Appointment
        fields = ['status', 'appointment_date', 'start_time', 'end_time', 'notes', 'location', 'estimated_cost']
    
    def validate(self, data):
        """Validate the updated appointment data"""
        instance = self.instance
        appointment_date = data.get('appointment_date', instance.appointment_date)
        start_time = data.get('start_time', instance.start_time)
        end_time = data.get('end_time', instance.end_time)
        
        # If rescheduling, check availability
        if 'appointment_date' in data or 'start_time' in data or 'end_time' in data:
            contractor = instance.contractor
            
            # Check if the contractor is available on this date
            if UnavailableDate.objects.filter(contractor=contractor, date=appointment_date).exists():
                raise serializers.ValidationError("The contractor is not available on this date")
            
            # Check if the time slot falls within the contractor's availability
            day_of_week = appointment_date.weekday()
            available_slots = AvailabilitySlot.objects.filter(
                contractor=contractor,
                day_of_week=day_of_week,
                start_time__lte=start_time,
                end_time__gte=end_time
            )
            
            if not available_slots.exists():
                raise serializers.ValidationError("The contractor is not available during this time slot")
            
            # Check for overlapping appointments (excluding this one)
            overlapping_appointments = Appointment.objects.filter(
                contractor=contractor,
                appointment_date=appointment_date,
                status__in=['REQUESTED', 'CONFIRMED'],
            ).exclude(id=instance.id).filter(
                # Check for time overlap
                models.Q(start_time__lt=end_time, end_time__gt=start_time)
            )
            
            if overlapping_appointments.exists():
                raise serializers.ValidationError("The contractor already has an appointment during this time")
        
        return data
