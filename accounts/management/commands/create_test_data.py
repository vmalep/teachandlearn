from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from profiles.models import Profile
from teachers.models import ClassOffering, TeacherProfile
from students.models import StudentProfile, StudentSubject
from subjects.models import Subject


USERS = [
    {
        "email": "alice@test.com",
        "first_name": "Alice",
        "last_name": "Dupont",
        "role": "teacher",
        "teacher": {
            "subjects": ["French", "English"],
            "native_language": "French",
            "price_per_hour": 35,
            "teaching_mode": "both",
            "availability": "Weekday evenings and Saturday mornings",
            "availability_schedule": {
                "mon": {"morning": False, "afternoon": False, "evening": True},
                "tue": {"morning": False, "afternoon": False, "evening": True},
                "wed": {"morning": False, "afternoon": False, "evening": True},
                "thu": {"morning": False, "afternoon": False, "evening": True},
                "fri": {"morning": False, "afternoon": False, "evening": True},
                "sat": {"morning": True, "afternoon": False, "evening": False},
                "sun": {"morning": False, "afternoon": False, "evening": False},
            },
            "state": "validated",
            "offerings": [
                {"subject": "French", "teaching_mode": "presential", "format": "individual",
                 "level": "all", "price_per_hour": 35, "is_active": True},
                {"subject": "English", "teaching_mode": "online", "format": "group",
                 "level": "intermediate", "price_per_hour": 25,
                 "description": "Conversation practice", "is_active": True},
            ],
        },
        "profile": {
            "bio": "Certified French teacher with 10 years of experience in Brussels.",
            "municipality": "Ixelles",
            "postal_code": "1050",
            "street": "Rue de la Paix",
            "house_number": "12",
        },
    },
    {
        "email": "bob@test.com",
        "first_name": "Bob",
        "last_name": "Janssen",
        "role": "teacher",
        "teacher": {
            "subjects": ["Dutch", "German"],
            "native_language": "Dutch",
            "price_per_hour": 40,
            "teaching_mode": "presential",
            "availability": "Flexible schedule",
            "availability_schedule": {
                "mon": {"morning": True, "afternoon": True, "evening": False},
                "tue": {"morning": True, "afternoon": True, "evening": False},
                "wed": {"morning": True, "afternoon": True, "evening": False},
                "thu": {"morning": True, "afternoon": True, "evening": False},
                "fri": {"morning": True, "afternoon": True, "evening": False},
                "sat": {"morning": False, "afternoon": False, "evening": False},
                "sun": {"morning": False, "afternoon": False, "evening": False},
            },
            "state": "draft",
        },
        "profile": {
            "bio": "Native Dutch speaker offering lessons in Ghent area.",
            "municipality": "Gent",
            "postal_code": "9000",
            "street": "Korenmarkt",
            "house_number": "5",
        },
    },
    {
        "email": "carlos@test.com",
        "first_name": "Carlos",
        "last_name": "García",
        "role": "teacher",
        "teacher": {
            "subjects": ["Spanish"],
            "native_language": "Spanish",
            "price_per_hour": 30,
            "teaching_mode": "online",
            "availability": "Weekends only",
            "availability_schedule": {
                "mon": {"morning": False, "afternoon": False, "evening": False},
                "tue": {"morning": False, "afternoon": False, "evening": False},
                "wed": {"morning": False, "afternoon": False, "evening": False},
                "thu": {"morning": False, "afternoon": False, "evening": False},
                "fri": {"morning": False, "afternoon": False, "evening": False},
                "sat": {"morning": True, "afternoon": True, "evening": True},
                "sun": {"morning": True, "afternoon": True, "evening": True},
            },
            "state": "rejected",
            "rejection_reason": "ID document could not be verified.",
        },
        "profile": {
            "bio": "Spanish native from Madrid, teaching online.",
            "municipality": "Liège",
            "postal_code": "4000",
            "street": "Rue Léopold",
            "house_number": "8",
        },
    },
    {
        "email": "diana@test.com",
        "first_name": "Diana",
        "last_name": "Martin",
        "role": "student",
        "student": {
            "learning_goals": "I want to reach B2 level in French for professional use.",
            "subjects": [("French", "intermediate"), ("English", "advanced")],
        },
        "profile": {
            "bio": "Marketing professional looking to improve my French.",
            "municipality": "Bruxelles",
            "postal_code": "1000",
        },
    },
    {
        "email": "evan@test.com",
        "first_name": "Evan",
        "last_name": "Peeters",
        "role": "student",
        "student": {
            "learning_goals": "Beginner in Spanish, hoping to travel to South America.",
            "subjects": [("Spanish", "beginner"), ("Dutch", "elementary")],
        },
        "profile": {
            "bio": "Student at ULB, learning languages for fun.",
            "municipality": "Etterbeek",
            "postal_code": "1040",
        },
    },
    {
        "email": "fatima@test.com",
        "first_name": "Fatima",
        "last_name": "El Amrani",
        "role": "both",
        "teacher": {
            "subjects": ["Arabic"],
            "native_language": "Arabic",
            "price_per_hour": 25,
            "teaching_mode": "both",
            "availability": "Monday to Friday afternoons",
            "availability_schedule": {
                "mon": {"morning": False, "afternoon": True, "evening": False},
                "tue": {"morning": False, "afternoon": True, "evening": False},
                "wed": {"morning": False, "afternoon": True, "evening": False},
                "thu": {"morning": False, "afternoon": True, "evening": False},
                "fri": {"morning": False, "afternoon": True, "evening": False},
                "sat": {"morning": False, "afternoon": False, "evening": False},
                "sun": {"morning": False, "afternoon": False, "evening": False},
            },
            "state": "validated",
            "offerings": [
                {"subject": "Arabic", "teaching_mode": "both", "format": "individual",
                 "level": "all", "price_per_hour": 25, "is_active": True},
                {"subject": "Arabic", "teaching_mode": "online", "format": "group",
                 "level": "beginner", "price_per_hour": 15,
                 "description": "Group intro sessions", "is_active": False},
            ],
        },
        "student": {
            "learning_goals": "Improving my French writing skills.",
            "subjects": [("French", "upper_intermediate")],
        },
        "profile": {
            "bio": "Arabic teacher and French learner based in Molenbeek.",
            "municipality": "Molenbeek-Saint-Jean",
            "postal_code": "1080",
            "street": "Rue Fin",
            "house_number": "3",
        },
    },
]


class Command(BaseCommand):
    help = "Create test users with teacher/student profiles"

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        skipped = 0

        for data in USERS:
            if User.objects.filter(email=data["email"]).exists():
                self.stdout.write(f"  skip  {data['email']} (already exists)")
                skipped += 1
                continue

            user = User.objects.create_user(
                email=data["email"],
                password="test1234",
                first_name=data["first_name"],
                last_name=data["last_name"],
                email_verified=True,
            )

            pd = data["profile"]
            profile = user.profile  # created by post_save signal
            profile.is_teacher = data["role"] in ("teacher", "both")
            profile.is_student = data["role"] in ("student", "both")
            profile.bio = pd.get("bio", "")
            profile.municipality = pd.get("municipality", "")
            profile.postal_code = pd.get("postal_code", "")
            profile.street = pd.get("street", "")
            profile.house_number = pd.get("house_number", "")
            profile.save()

            if data["role"] in ("teacher", "both"):
                td = data["teacher"]
                tp = TeacherProfile.objects.create(
                    profile=profile,
                    native_language=td.get("native_language", ""),
                    price_per_hour=td.get("price_per_hour"),
                    teaching_mode=td.get("teaching_mode", "both"),
                    availability=td.get("availability", ""),
                    availability_schedule=td.get("availability_schedule", {}),
                    state=td.get("state", "draft"),
                    rejection_reason=td.get("rejection_reason", ""),
                )
                for subject_name in td.get("subjects", []):
                    subject = Subject.objects.filter(name=subject_name).first()
                    if subject:
                        tp.subjects.add(subject)
                for offering_data in td.get("offerings", []):
                    od = {**offering_data}
                    subject_name = od.pop("subject")
                    subject = Subject.objects.filter(name=subject_name).first()
                    if subject:
                        ClassOffering.objects.create(teacher=tp, subject=subject, **od)

            if data["role"] in ("student", "both"):
                sd = data["student"]
                sp = StudentProfile.objects.create(
                    profile=profile,
                    learning_goals=sd.get("learning_goals", ""),
                )
                for subject_name, level in sd.get("subjects", []):
                    subject = Subject.objects.filter(name=subject_name).first()
                    if subject:
                        StudentSubject.objects.create(
                            student=sp, subject=subject, level=level
                        )

            self.stdout.write(f"  created {data['email']} ({data['role']})")
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone: {created} created, {skipped} skipped."
        ))
