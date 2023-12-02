from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer

@api_view(['GET'])
def getRoutes(request):
    routes=[
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms=Room.objects.all()    #python objects returned, it cant be directly converted to json sp serialize
    serializer = RoomSerializer(rooms, many=True)   #many objects may be serialized so true
    return Response(serializer.data)

@api_view(['GET'])
def getRoom(request,pk):
    room=Room.objects.get(id=pk)    #python objects returned, it cant be directly converted to json sp serialize
    serializer = RoomSerializer(room, many=False)   #specific objects  to be serialized so false
    return Response(serializer.data)