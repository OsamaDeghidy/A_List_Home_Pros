import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker

from users.models import UserRole
from contractors.models import ServiceCategory, ContractorProfile, ContractorPortfolio, ContractorReview
from scheduling.models import AvailabilitySlot, UnavailableDate, Appointment, AppointmentNote
from messaging.models import Conversation, Message, Notification
from analytics.models import DashboardStat, ContractorStat, ServiceCategoryStat, UserActivity, SearchQuery
from notifications.models import NotificationTemplate, NotificationSetting, Notification as SystemNotification

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Creates test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clients',
            type=int,
            default=10,
            help='Number of client users to create'
        )
        parser.add_argument(
            '--contractors',
            type=int,
            default=20,
            help='Number of contractor users to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )

    def handle(self, *args, **options):
        num_clients = options['clients']
        num_contractors = options['contractors']
        clear_data = options['clear']

        self.stdout.write(self.style.SUCCESS(f'Creating test data: {num_clients} clients, {num_contractors} contractors'))
        
        if clear_data:
            self.clear_data()
        
        with transaction.atomic():
            # Create service categories
            categories = self.create_service_categories()
            
            # Create admin user if it doesn't exist
            admin_user = self.create_admin_user()
            
            # Create client users
            client_users = self.create_users(num_clients, UserRole.CLIENT)
            self.stdout.write(self.style.SUCCESS(f'Created {len(client_users)} client users'))
            
            # Create contractor users and profiles
            contractor_users = self.create_users(num_contractors, UserRole.CONTRACTOR)
            contractor_profiles = self.create_contractor_profiles(contractor_users, categories)
            self.stdout.write(self.style.SUCCESS(f'Created {len(contractor_profiles)} contractor profiles'))
            
            # Create availability slots for contractors
            self.create_availability_slots(contractor_profiles)
            
            # Create unavailable dates for contractors
            self.create_unavailable_dates(contractor_profiles)
            
            # Create appointments between clients and contractors
            appointments = self.create_appointments(client_users, contractor_profiles)
            self.stdout.write(self.style.SUCCESS(f'Created {len(appointments)} appointments'))
            
            # Create appointment notes
            self.create_appointment_notes(appointments)
            
            # Create conversations and messages
            conversations = self.create_conversations(client_users, contractor_users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(conversations)} conversations'))
            
            # Create notification templates
            templates = self.create_notification_templates()
            
            # Create notification settings for users
            self.create_notification_settings(client_users + contractor_users)
            
            # Create system notifications
            self.create_system_notifications(client_users + contractor_users)
            
            # Create analytics data
            self.create_analytics_data(contractor_profiles, categories)
            
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))

    def clear_data(self):
        """Clear existing test data"""
        self.stdout.write('Clearing existing test data...')
        
        # Preserve admin users and real data
        admin_emails = ['admin@example.com', 'admin@alistpros.com']
        
        # Delete test users and related data
        User.objects.exclude(email__in=admin_emails).delete()
        
        # Delete other test data
        ServiceCategory.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Existing test data cleared'))

    def create_admin_user(self):
        """Create admin user if it doesn't exist"""
        email = 'admin@alistpros.com'
        password = 'adminpassword123'
        
        try:
            admin_user = User.objects.get(email=email)
            self.stdout.write(f'Admin user {email} already exists')
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                email=email,
                password=password,
                name='Admin User',
                role=UserRole.ADMIN,
                is_staff=True,
                is_superuser=True,
                is_active=True,
                email_verified=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {email}'))
        
        return admin_user

    def create_service_categories(self):
        """Create service categories"""
        categories = [
            {'name': 'Plumbing', 'description': 'Plumbing services including repairs, installations, and maintenance'},
            {'name': 'Electrical', 'description': 'Electrical services including wiring, installations, and repairs'},
            {'name': 'HVAC', 'description': 'Heating, ventilation, and air conditioning services'},
            {'name': 'Carpentry', 'description': 'Carpentry services including furniture, structures, and repairs'},
            {'name': 'Painting', 'description': 'Interior and exterior painting services'},
            {'name': 'Landscaping', 'description': 'Landscaping and garden maintenance services'},
            {'name': 'Cleaning', 'description': 'Cleaning services for homes and offices'},
            {'name': 'Roofing', 'description': 'Roof installation, repair, and maintenance'},
            {'name': 'Flooring', 'description': 'Flooring installation and repair services'},
            {'name': 'General Contracting', 'description': 'General contracting and construction services'},
            {'name': 'Handyman', 'description': 'General handyman services for small repairs and maintenance'},
            {'name': 'Appliance Repair', 'description': 'Repair services for home appliances'},
        ]
        
        created_categories = []
        for category_data in categories:
            category, created = ServiceCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            created_categories.append(category)
            
            if created:
                self.stdout.write(f'Created service category: {category.name}')
            else:
                self.stdout.write(f'Service category already exists: {category.name}')
        
        return created_categories

    def create_users(self, count, role):
        """Create users with specified role"""
        created_users = []
        
        for i in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            name = f"{first_name} {last_name}"
            
            if role == UserRole.CLIENT:
                email = f"client{i+1}@example.com"
                password = f"client{i+1}password"
            else:
                email = f"contractor{i+1}@example.com"
                password = f"contractor{i+1}password"
            
            try:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    name=name,
                    role=role,
                    is_active=True,
                    email_verified=True,
                    phone_number=fake.phone_number(),
                    date_joined=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc)
                )
                
                # No need to create address as it's not in the model
                
                created_users.append(user)
                self.stdout.write(f'Created {role} user: {email}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {email}: {str(e)}'))
        
        return created_users

    # Address creation method removed as it's not in the model

    def create_contractor_profiles(self, contractor_users, categories):
        """Create contractor profiles"""
        created_profiles = []
        
        for user in contractor_users:
            try:
                # Create contractor profile
                profile = ContractorProfile.objects.create(
                    user=user,
                    business_name=fake.company(),
                    business_phone=fake.phone_number(),
                    business_email=user.email,
                    description=fake.paragraph(nb_sentences=5),
                    years_in_business=random.randint(1, 20),
                    is_verified=random.choice([True, False]),
                    is_insured=random.choice([True, False]),
                    is_licensed=random.choice([True, False]),
                    license_number=fake.bothify(text='??###???') if random.choice([True, False]) else '',
                    insurance_provider=fake.company() if random.choice([True, False]) else '',
                    insurance_policy_number=fake.bothify(text='???####???') if random.choice([True, False]) else '',
                    average_rating=random.uniform(3.0, 5.0)
                )
                
                # Add random service categories
                num_categories = random.randint(1, 3)
                selected_categories = random.sample(list(categories), num_categories)
                profile.service_categories.add(*selected_categories)
                
                # Create portfolio items
                self.create_portfolio_items(profile)
                
                # Create reviews
                self.create_reviews(profile)
                
                created_profiles.append(profile)
                self.stdout.write(f'Created contractor profile: {profile.business_name}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating contractor profile for {user.email}: {str(e)}'))
        
        return created_profiles

    def create_portfolio_items(self, contractor_profile):
        """Create portfolio items for contractor"""
        num_items = random.randint(2, 5)
        
        for i in range(num_items):
            ContractorPortfolio.objects.create(
                contractor=contractor_profile,
                title=fake.catch_phrase(),
                description=fake.paragraph(nb_sentences=3),
                project_date=fake.date_between(start_date='-2y', end_date='today'),
                project_cost=random.randint(500, 10000),
                image_url=f"https://picsum.photos/id/{random.randint(1, 1000)}/800/600"
            )

    def create_reviews(self, contractor_profile):
        """Create reviews for contractor"""
        num_reviews = random.randint(3, 10)
        
        # Get client users
        client_users = User.objects.filter(role=UserRole.CLIENT)
        
        if not client_users:
            return
        
        for i in range(num_reviews):
            client = random.choice(client_users)
            
            ContractorReview.objects.create(
                contractor=contractor_profile,
                client=client,
                rating=random.randint(3, 5),
                comment=fake.paragraph(nb_sentences=2),
                created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc)
            )

    def create_availability_slots(self, contractor_profiles):
        """Create availability slots for contractors"""
        days_of_week = list(range(7))  # 0 = Monday, 6 = Sunday
        
        for profile in contractor_profiles:
            # Create 3-5 availability slots per contractor
            num_slots = random.randint(3, 5)
            
            for i in range(num_slots):
                day = random.choice(days_of_week)
                start_hour = random.randint(8, 14)
                end_hour = start_hour + random.randint(2, 8)
                
                AvailabilitySlot.objects.create(
                    contractor=profile,
                    day_of_week=day,
                    start_time=time(start_hour, 0),
                    end_time=time(min(end_hour, 23), 0)
                )

    def create_unavailable_dates(self, contractor_profiles):
        """Create unavailable dates for contractors"""
        today = timezone.now().date()
        
        for profile in contractor_profiles:
            # Create 1-3 unavailable dates per contractor
            num_dates = random.randint(1, 3)
            
            for i in range(num_dates):
                start_date = today + timedelta(days=random.randint(1, 60))
                end_date = start_date + timedelta(days=random.randint(1, 5))
                
                UnavailableDate.objects.create(
                    contractor=profile,
                    start_date=start_date,
                    end_date=end_date,
                    reason=random.choice(['Vacation', 'Personal', 'Holiday', 'Other Project'])
                )

    def create_appointments(self, client_users, contractor_profiles):
        """Create appointments between clients and contractors"""
        created_appointments = []
        today = timezone.now().date()
        
        # Status distribution
        statuses = ['REQUESTED', 'CONFIRMED', 'COMPLETED', 'CANCELLED']
        status_weights = [0.2, 0.3, 0.4, 0.1]  # 20% requested, 30% confirmed, 40% completed, 10% cancelled
        
        # Create 30-50 appointments
        num_appointments = random.randint(30, 50)
        
        for i in range(num_appointments):
            client = random.choice(client_users)
            contractor_profile = random.choice(contractor_profiles)
            
            # Determine if appointment is in the past or future
            is_past = random.random() < 0.6  # 60% past, 40% future
            
            if is_past:
                days_offset = -random.randint(1, 90)
                status = random.choices(statuses, weights=[0, 0, 0.8, 0.2])[0]  # 80% completed, 20% cancelled
            else:
                days_offset = random.randint(1, 60)
                status = random.choices(statuses, weights=[0.4, 0.6, 0, 0])[0]  # 40% requested, 60% confirmed
            
            appointment_date = today + timedelta(days=days_offset)
            
            # Get a random hour between 8 AM and 5 PM
            start_hour = random.randint(8, 17)
            start_time = time(start_hour, 0)
            end_time = time(start_hour + random.randint(1, 3), 0)
            
            try:
                # Get a random service category for the contractor
                service_category = random.choice(list(contractor_profile.service_categories.all()))
                
                appointment = Appointment.objects.create(
                    client=client,
                    contractor=contractor_profile,
                    service_category=service_category,
                    appointment_date=appointment_date,
                    start_time=start_time,
                    end_time=end_time,
                    status=status,
                    notes=fake.paragraph(nb_sentences=2),
                    location=fake.address(),
                    estimated_cost=random.randint(50, 500),
                    created_at=fake.date_time_between(
                        start_date='-6m',
                        end_date=timezone.now() - timedelta(days=abs(days_offset) + 1 if days_offset < 0 else 0),
                        tzinfo=timezone.utc
                    )
                )
                
                created_appointments.append(appointment)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating appointment: {str(e)}'))
        
        return created_appointments

    def create_appointment_notes(self, appointments):
        """Create notes for appointments"""
        for appointment in appointments:
            # 70% chance to have a client note
            if random.random() < 0.7:
                AppointmentNote.objects.create(
                    appointment=appointment,
                    author=appointment.client,
                    note=fake.paragraph(nb_sentences=1),
                    is_private=False
                )
            
            # 80% chance to have a contractor note
            if random.random() < 0.8:
                AppointmentNote.objects.create(
                    appointment=appointment,
                    author=appointment.contractor.user,
                    note=fake.paragraph(nb_sentences=1),
                    is_private=random.random() < 0.3  # 30% chance to be private
                )

    def create_conversations(self, client_users, contractor_users):
        """Create conversations and messages between users"""
        created_conversations = []
        
        # Create 15-25 conversations
        num_conversations = random.randint(15, 25)
        
        for i in range(num_conversations):
            client = random.choice(client_users)
            contractor = random.choice(contractor_users)
            
            # Create conversation
            conversation = Conversation.objects.create(
                title=f"Project Discussion: {fake.bs()}"
            )
            conversation.participants.add(client, contractor)
            
            # Create 5-15 messages per conversation
            num_messages = random.randint(5, 15)
            
            for j in range(num_messages):
                # Alternate between client and contractor
                sender = client if j % 2 == 0 else contractor
                
                # Create message
                message = Message.objects.create(
                    conversation=conversation,
                    sender=sender,
                    content=fake.paragraph(nb_sentences=random.randint(1, 3)),
                    created_at=fake.date_time_between(
                        start_date='-3m',
                        end_date='now',
                        tzinfo=timezone.utc
                    )
                )
                
                # Mark some messages as read
                if random.random() < 0.8:  # 80% chance to be read
                    recipient = contractor if sender == client else client
                    message.read_by.add(recipient)
            
            created_conversations.append(conversation)
            
            # Create notification for the last message
            last_message = conversation.messages.order_by('-created_at').first()
            if last_message:
                recipient = contractor if last_message.sender == client else client
                
                Notification.objects.create(
                    user=recipient,
                    message=last_message,
                    read=random.random() < 0.5  # 50% chance to be read
                )
        
        return created_conversations

    def create_notification_templates(self):
        """Create notification templates"""
        templates = [
            {
                'name': 'appointment_reminder',
                'description': 'Reminder for upcoming appointments',
                'subject': 'Reminder: Your appointment is coming up',
                'email_body': """
                    <p>Hello {{ user.name }},</p>
                    <p>This is a reminder that you have an appointment scheduled for {{ appointment.appointment_date }} 
                    at {{ appointment.start_time }}.</p>
                    <p>Appointment details:</p>
                    <ul>
                        <li>Date: {{ appointment.appointment_date }}</li>
                        <li>Time: {{ appointment.start_time }} - {{ appointment.end_time }}</li>
                        <li>{% if user.role == 'CLIENT' %}Contractor: {{ appointment.contractor.business_name }}{% else %}Client: {{ appointment.client.name }}{% endif %}</li>
                        <li>Service: {{ appointment.service_description }}</li>
                    </ul>
                    <p>Thank you for using A-List Home Pros!</p>
                """,
                'sms_body': "Reminder: Your appointment is on {{ appointment.appointment_date }} at {{ appointment.start_time }}. Log in to A-List Home Pros for details.",
                'push_body': "Your appointment is coming up on {{ appointment.appointment_date }} at {{ appointment.start_time }}."
            },
            {
                'name': 'new_message',
                'description': 'Notification for new messages',
                'subject': 'New message from {{ message.sender.name }}',
                'email_body': """
                    <p>Hello {{ user.name }},</p>
                    <p>You have received a new message from {{ message.sender.name }}:</p>
                    <blockquote>{{ message.content }}</blockquote>
                    <p>Log in to your account to reply.</p>
                    <p>Thank you for using A-List Home Pros!</p>
                """,
                'sms_body': "New message from {{ message.sender.name }}. Log in to A-List Home Pros to view and reply.",
                'push_body': "{{ message.sender.name }}: {{ message.content|truncatechars:50 }}"
            },
            {
                'name': 'appointment_status_change',
                'description': 'Notification for appointment status changes',
                'subject': 'Your appointment status has been updated',
                'email_body': """
                    <p>Hello {{ user.name }},</p>
                    <p>The status of your appointment on {{ appointment.appointment_date }} has been updated to {{ appointment.status }}.</p>
                    <p>Appointment details:</p>
                    <ul>
                        <li>Date: {{ appointment.appointment_date }}</li>
                        <li>Time: {{ appointment.start_time }} - {{ appointment.end_time }}</li>
                        <li>{% if user.role == 'CLIENT' %}Contractor: {{ appointment.contractor.business_name }}{% else %}Client: {{ appointment.client.name }}{% endif %}</li>
                        <li>Status: {{ appointment.status }}</li>
                    </ul>
                    <p>Log in to your account for more details.</p>
                    <p>Thank you for using A-List Home Pros!</p>
                """,
                'sms_body': "Your appointment on {{ appointment.appointment_date }} has been updated to {{ appointment.status }}. Log in to A-List Home Pros for details.",
                'push_body': "Appointment status updated to {{ appointment.status }} for {{ appointment.appointment_date }}."
            },
        ]
        
        created_templates = []
        
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'subject': template_data['subject'],
                    'email_body': template_data['email_body'],
                    'sms_body': template_data['sms_body'],
                    'push_body': template_data['push_body'],
                }
            )
            
            created_templates.append(template)
            
            if created:
                self.stdout.write(f'Created notification template: {template.name}')
            else:
                self.stdout.write(f'Notification template already exists: {template.name}')
        
        return created_templates

    def create_notification_settings(self, users):
        """Create notification settings for users"""
        for user in users:
            NotificationSetting.objects.get_or_create(
                user=user,
                defaults={
                    'email_enabled': True,
                    'sms_enabled': random.choice([True, False]),
                    'push_enabled': True,
                    'new_message_email': True,
                    'new_message_sms': random.choice([True, False]),
                    'new_message_push': True,
                    'appointment_reminder_email': True,
                    'appointment_reminder_sms': random.choice([True, False]),
                    'appointment_reminder_push': True,
                    'appointment_status_change_email': True,
                    'appointment_status_change_sms': random.choice([True, False]),
                    'appointment_status_change_push': True,
                    'payment_email': True,
                    'payment_sms': random.choice([True, False]),
                    'payment_push': True,
                    'marketing_email': random.choice([True, False]),
                    'marketing_sms': False,
                    'marketing_push': random.choice([True, False]),
                }
            )

    def create_system_notifications(self, users):
        """Create system notifications for users"""
        notification_types = ['MESSAGE', 'APPOINTMENT', 'PAYMENT', 'SYSTEM', 'MARKETING']
        
        for user in users:
            # Create 5-10 notifications per user
            num_notifications = random.randint(5, 10)
            
            for i in range(num_notifications):
                notification_type = random.choice(notification_types)
                
                if notification_type == 'MESSAGE':
                    title = 'New message received'
                    message = f'You have received a new message from {fake.name()}'
                elif notification_type == 'APPOINTMENT':
                    title = 'Appointment update'
                    message = f'Your appointment on {fake.date_this_month()} has been {random.choice(["confirmed", "rescheduled", "cancelled"])}'
                elif notification_type == 'PAYMENT':
                    title = 'Payment update'
                    message = f'Your payment of ${random.randint(50, 500)} has been {random.choice(["processed", "received", "refunded"])}'
                elif notification_type == 'SYSTEM':
                    title = 'System notification'
                    message = f'Your account has been {random.choice(["updated", "verified", "accessed from a new device"])}'
                else:  # MARKETING
                    title = 'Special offer'
                    message = f'Check out our new {random.choice(["feature", "service", "promotion"])} available now!'
                
                # Create notification
                SystemNotification.objects.create(
                    user=user,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    read=random.random() < 0.6,  # 60% chance to be read
                    read_at=timezone.now() if random.random() < 0.6 else None,
                    created_at=fake.date_time_between(start_date='-3m', end_date='now', tzinfo=timezone.utc)
                )

    def create_analytics_data(self, contractor_profiles, categories):
        """Create analytics data"""
        # Create dashboard stats for the last 30 days
        today = timezone.now().date()
        
        for i in range(30):
            date = today - timedelta(days=i)
            
            DashboardStat.objects.create(
                date=date,
                new_users=random.randint(1, 10),
                new_contractors=random.randint(0, 3),
                new_appointments=random.randint(2, 15),
                completed_appointments=random.randint(1, 10),
                total_payment_volume=random.randint(500, 5000)
            )
        
        # Create contractor stats
        for profile in contractor_profiles:
            for i in range(7):  # Last 7 days
                date = today - timedelta(days=i)
                
                ContractorStat.objects.create(
                    contractor=profile,
                    date=date,
                    profile_views=random.randint(5, 50),
                    appointment_requests=random.randint(0, 5),
                    completed_appointments=random.randint(0, 3),
                    cancelled_appointments=random.randint(0, 1),
                    total_earnings=random.randint(0, 1000),
                    average_rating=random.uniform(3.5, 5.0)
                )
        
        # Create service category stats
        for category in categories:
            for i in range(7):  # Last 7 days
                date = today - timedelta(days=i)
                
                ServiceCategoryStat.objects.create(
                    service_category=category,
                    date=date,
                    contractor_count=random.randint(1, 10),
                    appointment_count=random.randint(0, 20),
                    average_price=random.randint(50, 500)
                )
        
        # Create user activities
        users = User.objects.all()
        activity_types = ['LOGIN', 'PROFILE_UPDATE', 'SEARCH', 'VIEW_CONTRACTOR', 'BOOK_APPOINTMENT', 'PAYMENT']
        
        for i in range(100):  # Create 100 user activities
            user = random.choice(users)
            activity_type = random.choice(activity_types)
            
            UserActivity.objects.create(
                user=user,
                activity_type=activity_type,
                description=f'{user.name} performed {activity_type}',
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                created_at=fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.utc)
            )
        
        # Create search queries
        for i in range(50):  # Create 50 search queries
            user = random.choice(users) if random.random() < 0.8 else None  # 80% chance to have a user
            
            SearchQuery.objects.create(
                user=user,
                query=random.choice([
                    'plumber', 'electrician', 'painter', 'carpenter', 'handyman',
                    'roof repair', 'bathroom remodel', 'kitchen renovation',
                    'fence installation', 'deck building', 'landscaping'
                ]),
                filters={
                    'location': fake.city(),
                    'rating': random.randint(3, 5),
                    'price_range': f'{random.randint(50, 200)}-{random.randint(200, 500)}'
                },
                results_count=random.randint(0, 20),
                created_at=fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.utc)
            )
