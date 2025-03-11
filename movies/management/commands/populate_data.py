from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from movies.models import Movie, Theater, Showing
from inventory.models import SnackItem
from datetime import timedelta
import random
import decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Clear existing data
        self.clear_data()
        
        # Create users
        self.create_users()
        
        # Create movies
        movies = self.create_movies()
        
        # Create theaters
        theaters = self.create_theaters()
        
        # Create showings
        self.create_showings(movies, theaters)
        
        # Create snack items
        self.create_snacks()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
    
    def clear_data(self):
        """Clear existing data from the database"""
        self.stdout.write('Clearing existing data...')
        Showing.objects.all().delete()
        Movie.objects.all().delete()
        Theater.objects.all().delete()
        SnackItem.objects.all().delete()
        # Don't delete users, as you might have created a superuser already
    
    def create_users(self):
        """Create sample users"""
        self.stdout.write('Creating users...')
        
        # Create a regular user
        if not User.objects.filter(username='customer').exists():
            User.objects.create_user(
                username='customer',
                email='customer@example.com',
                password='password123',
                is_staff_member=False
            )
        
        # Create a staff member
        if not User.objects.filter(username='staff').exists():
            User.objects.create_user(
                username='staff',
                email='staff@example.com',
                password='password123',
                is_staff=True,
                is_staff_member=True
            )
    
    def create_movies(self):
        """Create sample movies"""
        self.stdout.write('Creating movies...')
        
        movies_data = [
            {
                'title': 'The Space Odyssey',
                'description': 'A thrilling journey through the cosmos that challenges our understanding of space and time.',
                'duration': 142,
                'poster_url': 'https://example.com/posters/space_odyssey.jpg'
            },
            {
                'title': 'Midnight Mystery',
                'description': 'A detective must solve a complex murder case before the clock strikes midnight.',
                'duration': 115,
                'poster_url': 'https://example.com/posters/midnight_mystery.jpg'
            },
            {
                'title': 'The Last Adventure',
                'description': 'An epic tale of courage and friendship as heroes embark on their final quest.',
                'duration': 165,
                'poster_url': 'https://example.com/posters/last_adventure.jpg'
            },
            {
                'title': 'Digital Dreams',
                'description': 'When virtual reality becomes indistinguishable from reality, one programmer must find a way back.',
                'duration': 128,
                'poster_url': 'https://example.com/posters/digital_dreams.jpg'
            },
            {
                'title': 'Love in Paris',
                'description': 'A romantic comedy about finding love in the most unexpected places.',
                'duration': 110,
                'poster_url': 'https://example.com/posters/love_paris.jpg'
            }
        ]
        
        created_movies = []
        for movie_data in movies_data:
            movie = Movie.objects.create(**movie_data)
            created_movies.append(movie)
            self.stdout.write(f'Created movie: {movie.title}')
        
        return created_movies
    
    def create_theaters(self):
        """Create sample theaters"""
        self.stdout.write('Creating theaters...')
        
        theaters_data = [
            {
                'name': 'Grand Theater',
                'capacity': 200
            },
            {
                'name': 'IMAX Experience',
                'capacity': 150
            },
            {
                'name': 'Cozy Cinema',
                'capacity': 80
            },
            {
                'name': 'VIP Screening Room',
                'capacity': 40
            }
        ]
        
        created_theaters = []
        for theater_data in theaters_data:
            theater = Theater.objects.create(**theater_data)
            created_theaters.append(theater)
            self.stdout.write(f'Created theater: {theater.name}')
        
        return created_theaters
    
    def create_showings(self, movies, theaters):
        """Create sample showings for the next 7 days"""
        self.stdout.write('Creating showings...')
        
        # Time slots for showings
        time_slots = [
            (10, 0),  # 10:00 AM
            (13, 30), # 1:30 PM
            (16, 0),  # 4:00 PM
            (19, 30), # 7:30 PM
            (22, 0)   # 10:00 PM
        ]
        
        # Create showings for the next 7 days
        now = timezone.now()
        for day in range(7):
            current_date = now.date() + timedelta(days=day)
            
            # For each theater, create showings at different time slots
            for theater in theaters:
                # Randomly select 2-3 time slots for this theater on this day
                selected_slots = random.sample(time_slots, random.randint(2, 3))
                
                for hour, minute in selected_slots:
                    # Randomly select a movie
                    movie = random.choice(movies)
                    
                    # Calculate start and end times
                    start_time = timezone.make_aware(
                        timezone.datetime.combine(current_date, timezone.datetime.min.time()) + 
                        timedelta(hours=hour, minutes=minute)
                    )
                    end_time = start_time + timedelta(minutes=movie.duration)
                    
                    # Generate a random price between $8.50 and $15.00
                    price = decimal.Decimal(random.uniform(8.5, 15.0)).quantize(decimal.Decimal('0.01'))
                    
                    # Create the showing
                    showing = Showing.objects.create(
                        movie=movie,
                        theater=theater,
                        start_time=start_time,
                        end_time=end_time,
                        price=price
                    )
                    
                    self.stdout.write(f'Created showing: {movie.title} at {theater.name} on {start_time.strftime("%Y-%m-%d %H:%M")}')
    
    def create_snacks(self):
        """Create sample snack items"""
        self.stdout.write('Creating snack items...')
        
        snacks_data = [
            {
                'name': 'Large Popcorn',
                'description': 'Freshly popped buttery popcorn in a large bucket',
                'price': decimal.Decimal('7.99'),
                'quantity_available': 100
            },
            {
                'name': 'Medium Popcorn',
                'description': 'Freshly popped buttery popcorn in a medium bucket',
                'price': decimal.Decimal('5.99'),
                'quantity_available': 150
            },
            {
                'name': 'Nachos with Cheese',
                'description': 'Crispy tortilla chips with warm cheese sauce',
                'price': decimal.Decimal('6.50'),
                'quantity_available': 80
            },
            {
                'name': 'Large Soda',
                'description': 'Your choice of soda in a large cup',
                'price': decimal.Decimal('4.99'),
                'quantity_available': 200
            },
            {
                'name': 'Candy Box',
                'description': 'Assorted movie theater candy',
                'price': decimal.Decimal('3.99'),
                'quantity_available': 120
            },
            {
                'name': 'Hot Dog',
                'description': 'Classic hot dog with condiments',
                'price': decimal.Decimal('5.50'),
                'quantity_available': 60
            },
            {
                'name': 'Ice Cream',
                'description': 'Vanilla, chocolate, or strawberry ice cream cup',
                'price': decimal.Decimal('4.50'),
                'quantity_available': 70
            }
        ]
        
        for snack_data in snacks_data:
            snack = SnackItem.objects.create(**snack_data)
            self.stdout.write(f'Created snack item: {snack.name}')
