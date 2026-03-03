import requests
import heapq

def get_distance(loc1, loc2):
    # Compute the Euclidean distance between two locations
    return ((loc1['lat'] - loc2['lat'])**2 + (loc1['lon'] - loc2['lon'])**2)**0.5

def dijkstra(graph, start):
    # Implements Dijkstra's algorithm to find shortest paths from start node
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_distance > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances

def get_nearby_hospitals(location, radius=5000, limit=15):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
      way["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
      relation["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
    );
    out body;
    >;
    out skel qt;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    
    hospitals = []
    graph = {}
    
    for element in data['elements']:
        if element['type'] == 'node':
            hospital = {
                'name': element.get('tags', {}).get('name', 'N/A'),
                'address': element.get('tags', {}).get('address', 'N/A'),
                'location': {
                    'lat': element['lat'],
                    'lon': element['lon']
                }
            }
            hospitals.append(hospital)
            graph[(element['lat'], element['lon'])] = []
        
        elif element['type'] in ['way', 'relation']:
            for member in element.get('members', []):
                if member['type'] == 'node':
                    node_id = member['ref']
                    node = next((item for item in data['elements'] if item['id'] == node_id and item['type'] == 'node'), None)
                    if node:
                        graph[(node['lat'], node['lon'])] = []
    
    # Add edges to the graph based on distances between nodes
    for node1 in graph:
        for node2 in graph:
            if node1 != node2:
                distance = get_distance({'lat': node1[0], 'lon': node1[1]}, {'lat': node2[0], 'lon': node2[1]})
                graph[node1].append((node2, distance))
    
    # Perform Dijkstra's algorithm to find shortest paths from the starting location
    distances = dijkstra(graph, (location[0], location[1]))
    
    # Sort hospitals by their distance from the start location
    hospitals.sort(key=lambda h: get_distance(location, h['location']))
    
    return hospitals[:limit]
