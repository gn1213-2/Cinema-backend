from rest_framework import serializers
from .models import Movie, Theater, Showing, Booking
from datetime import timedelta

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = '__all__'

class ShowingSerializer(serializers.ModelSerializer):
    movie_title = serializers.SerializerMethodField()
    theater_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Showing
        fields = ['id', 'movie', 'theater', 'start_time', 'end_time', 'price', 'movie_title', 'theater_name']
    
    def get_movie_title(self, obj):
        return obj.movie.title if obj.movie else None
    
    def get_theater_name(self, obj):
        return obj.theater.name if obj.theater else None
    
    def validate(self, data):
        """
        Calculate end_time based on movie duration
        """
        if 'movie' in data and 'start_time' in data:
            movie = data['movie']
            start_time = data['start_time']
            
            # Calculate end time based on movie duration
            duration_minutes = movie.duration
            end_time = start_time + timedelta(minutes=duration_minutes)
            data['end_time'] = end_time
        
        return data
    
    def to_representation(self, instance):
        """
        Add additional fields to the serialized data
        """
        data = super().to_representation(instance)
        
        # Ensure these fields are always present
        if 'movie_title' not in data or data['movie_title'] is None:
            data['movie_title'] = instance.movie.title if instance.movie else 'Unknown Movie'
            
        if 'theater_name' not in data or data['theater_name'] is None:
            data['theater_name'] = instance.theater.name if instance.theater else 'Unknown Theater'
            
        return data

class BookingSerializer(serializers.ModelSerializer):
    showing_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'seats', 'showing', 'showing_details', 'created_at']
    
    def get_showing_details(self, obj):
        try:
            return {
                'movie_title': obj.showing.movie.title,
                'theater_name': obj.showing.theater.name,
                'start_time': obj.showing.start_time.strftime('%Y-%m-%d %H:%M'),
                'end_time': obj.showing.end_time.strftime('%Y-%m-%d %H:%M') if obj.showing.end_time else None,
                'price': float(obj.showing.price)
            }
        except Exception as e:
            print(f"Error getting showing details: {str(e)}")
            return {
                'movie_title': 'Unknown',
                'theater_name': 'Unknown',
                'start_time': 'Unknown',
                'end_time': 'Unknown',
                'price': 0.0
            }