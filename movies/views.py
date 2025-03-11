from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Movie, Showing, Booking, Theater
from .serializers import MovieSerializer, ShowingSerializer, BookingSerializer, TheaterSerializer

# Create your views here.

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class ShowingViewSet(viewsets.ModelViewSet):
    queryset = Showing.objects.all().select_related('movie', 'theater')
    serializer_class = ShowingSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        try:
            showings = self.get_queryset()
            serializer = self.get_serializer(showings, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error listing showings: {str(e)}")
            return Response(
                {"detail": f"Failed to list showings: {str(e)}"},
                status=500
            )
    
    def create(self, request, *args, **kwargs):
        try:
            print(f"Creating showing with data: {request.data}")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"Error creating showing: {str(e)}")
            return Response(
                {"detail": f"Failed to create showing: {str(e)}"},
                status=400
            )
    
    def update(self, request, *args, **kwargs):
        try:
            print(f"Updating showing with data: {request.data}")
            return super().update(request, *args, **kwargs)
        except Exception as e:
            print(f"Error updating showing: {str(e)}")
            return Response(
                {"detail": f"Failed to update showing: {str(e)}"},
                status=400
            )

class TheaterViewSet(viewsets.ModelViewSet):
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

@api_view(['GET'])
def today_showings(request):
    try:
        # Get current date in server's timezone
        today = timezone.now().date()
        
        # Debug the date we're using
        print(f"Fetching showings for date: {today}")
        
        # Instead of filtering by date range, let's just get all showings
        # and then filter them in Python to debug the issue
        all_showings = Showing.objects.all().select_related('movie', 'theater')
        print(f"Total showings in database: {all_showings.count()}")
        
        # Now filter for today's date
        showings = []
        for showing in all_showings:
            showing_date = showing.start_time.date()
            print(f"Showing ID {showing.id}: date={showing_date}, today={today}")
            if showing_date == today:
                showings.append(showing)
        
        print(f"Found {len(showings)} showings for today after filtering")
        
        # If we still have no showings, let's be more lenient and include tomorrow's showings too
        if not showings:
            print("No showings found for today, including tomorrow's showings")
            tomorrow = today + timedelta(days=1)
            for showing in all_showings:
                showing_date = showing.start_time.date()
                if showing_date == tomorrow:
                    showings.append(showing)
        
        # If we still have no showings, let's just return all showings for debugging
        if not showings and all_showings.exists():
            print("Returning all showings for debugging")
            showings = list(all_showings)
        
        # Debug the first showing if any exist
        if showings:
            first_showing = showings[0]
            print(f"First showing: ID={first_showing.id}, Movie: {first_showing.movie.title}, Theater: {first_showing.theater.name}, Time: {first_showing.start_time}")
        
        serializer = ShowingSerializer(showings, many=True)
        return Response(serializer.data)
    except Exception as e:
        import traceback
        print(f"Error in today_showings: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {"error": f"Failed to fetch today's showings: {str(e)}"},
            status=500
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_showing(request):
    showing_id = request.data.get('showing_id')
    seats = request.data.get('seats')
    
    try:
        showing = Showing.objects.get(id=showing_id)
        
        # Create the booking
        booking = Booking.objects.create(
            user=request.user,
            showing=showing,
            seats=seats
        )
        
        # Debug print
        print(f"Created booking: {booking}")
        
        # Return more complete data
        serializer = BookingSerializer(booking)
        return Response({
            'success': True, 
            'booking_id': booking.id,
            'booking': serializer.data
        })
    except Showing.DoesNotExist:
        return Response({'error': 'Showing not found'}, status=404)
    except Exception as e:
        print(f"Error creating booking: {str(e)}")
        return Response({'error': f'Failed to create booking: {str(e)}'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookings(request):
    try:
        # Add debug print statements
        print(f"Fetching bookings for user: {request.user.username}")
        
        # Make sure the Booking model has the right fields and use prefetch_related for optimization
        bookings = Booking.objects.filter(user=request.user).select_related(
            'showing', 
            'showing__movie', 
            'showing__theater'
        ).order_by('-created_at')  # Show newest bookings first
        
        print(f"Found {bookings.count()} bookings")
        
        # Debug the first booking if any exist
        if bookings.exists():
            first_booking = bookings.first()
            print(f"First booking: {first_booking.id}, Showing: {first_booking.showing}, Created: {first_booking.created_at}")
            print(f"Showing details: Movie: {first_booking.showing.movie.title}, Theater: {first_booking.showing.theater.name}")
        
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    except Exception as e:
        # Log the error
        import traceback
        print(f"Error in user_bookings: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {"error": f"Failed to fetch bookings: {str(e)}"},
            status=500
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_test_showings(request):
    try:
        # Check if user is staff
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {"error": "You don't have permission to perform this action."},
                status=403
            )
            
        # Get counts before deletion
        showing_count = Showing.objects.count()
        booking_count = Booking.objects.count()
        
        # Delete all bookings first (to maintain referential integrity)
        Booking.objects.all().delete()
        
        # Then delete all showings
        Showing.objects.all().delete()
        
        # Log the operation
        print(f"Admin {request.user.username} removed {booking_count} bookings and {showing_count} showings")
        
        return Response({
            'success': True,
            'message': f'Successfully removed {showing_count} showings and {booking_count} bookings'
        })
    except Exception as e:
        print(f"Error removing test data: {str(e)}")
        return Response({
            'error': f'Failed to remove test data: {str(e)}'
        }, status=500)

@api_view(['GET'])
def debug_showings(request):
    """
    Debug endpoint to check all showings in the database
    """
    try:
        all_showings = Showing.objects.all().select_related('movie', 'theater')
        
        debug_data = []
        for showing in all_showings:
            debug_data.append({
                'id': showing.id,
                'movie_id': showing.movie.id if showing.movie else None,
                'movie_title': showing.movie.title if showing.movie else None,
                'theater_id': showing.theater.id if showing.theater else None,
                'theater_name': showing.theater.name if showing.theater else None,
                'start_time': showing.start_time.isoformat() if showing.start_time else None,
                'end_time': showing.end_time.isoformat() if showing.end_time else None,
                'price': float(showing.price) if showing.price else None,
                'start_time_date': showing.start_time.date().isoformat() if showing.start_time else None,
                'today': timezone.now().date().isoformat()
            })
        
        return Response({
            'count': len(debug_data),
            'today': timezone.now().date().isoformat(),
            'showings': debug_data
        })
    except Exception as e:
        import traceback
        print(f"Error in debug_showings: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {"error": f"Failed to fetch debug showings: {str(e)}"},
            status=500
        )
