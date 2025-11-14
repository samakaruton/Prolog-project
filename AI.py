"""
Jamaican Rural Road Network - Standalone Graphical User Interface
GUI implementation using Tkinter for the pathfinding system

This is a standalone version that includes all necessary components.
No need to run CLI first - just run this file directly!
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pyswip import Prolog
import os
from typing import List, Dict, Optional


class JamaicaRoadNetwork:
    """
    Backend class for managing the Jamaican road network system.
    Handles interaction between Python interface and Prolog backend.
    """
    
    def __init__(self, prolog_file: str = "road_network.pl"):
        """
        Initialize the road network system.
        
        Args:
            prolog_file: Path to the Prolog knowledge base file
        """
        self.prolog = Prolog()
        self.prolog_file = prolog_file
        self.load_prolog_file()
        
    def load_prolog_file(self):
        """Load the Prolog knowledge base."""
        if os.path.exists(self.prolog_file):
            self.prolog.consult(self.prolog_file)
            print(f"✓ Loaded Prolog knowledge base: {self.prolog_file}")
        else:
            print(f"⚠ Warning: {self.prolog_file} not found. Creating new file...")
            self.create_default_network()
    
    def create_default_network(self):
        """Create a default Jamaican road network with sample data."""
        default_data = """
% Jamaican Rural Road Network Knowledge Base
% Facts: road(Source, Destination, Distance_Km, Type, Status)

% Sample Jamaican rural network
road(morant_bay, port_morant, 12, paved, open).
road(port_morant, golden_grove, 8, unpaved, open).
road(golden_grove, bath, 15, paved, open).
road(bath, port_antonio, 25, paved, open).
road(morant_bay, yallahs, 10, unpaved, open).
road(yallahs, bath, 18, paved, open).
road(port_morant, port_antonio, 35, unpaved, closed).
road(golden_grove, manchioneal, 20, paved, open).
road(manchioneal, port_antonio, 12, paved, open).
road(morant_bay, eleven_mile, 6, paved, open).
road(eleven_mile, yallahs, 5, unpaved, open).
road(bath, stony_gut, 8, unpaved, open).
road(stony_gut, golden_grove, 10, paved, open).

% Road conditions (additional facts)
road_condition(port_morant, golden_grove, deep_potholes).
road_condition(morant_bay, yallahs, broken_cisterns).
road_condition(bath, stony_gut, deep_potholes).

% Bidirectional roads (symmetric)
road(B, A, Dist, Type, Status) :- road(A, B, Dist, Type, Status).
road_condition(B, A, Condition) :- road_condition(A, B, Condition).

% Average speeds by road type (km/h)
speed(paved, 60).
speed(unpaved, 30).

% Travel time calculation
travel_time(Source, Dest, Time) :-
    road(Source, Dest, Distance, Type, open),
    speed(Type, Speed),
    Time is Distance / Speed * 60.

% Helper: Check if road exists
road_exists(A, B) :- road(A, B, _, _, _).

% Helper: Get all locations
location(L) :- road(L, _, _, _, _).
location(L) :- road(_, L, _, _, _).

% Dijkstra's Algorithm Implementation
shortest_path(Start, End, Path, TotalDistance) :-
    dijkstra([[Start]], End, Path, TotalDistance).

dijkstra([[End|Path]|_], End, FinalPath, Distance) :-
    reverse([End|Path], FinalPath),
    calculate_distance(FinalPath, Distance).

dijkstra([Current|Queue], End, Path, Distance) :-
    Current = [Node|_],
    findall([Next, Node|Current],
            (road(Node, Next, _, _, open),
             \\+ member(Next, Current)),
            Extensions),
    append(Queue, Extensions, NewQueue),
    sort_paths(NewQueue, SortedQueue),
    dijkstra(SortedQueue, End, Path, Distance).

calculate_distance([_], 0).
calculate_distance([A, B|Rest], Total) :-
    road(A, B, Dist, _, _),
    calculate_distance([B|Rest], RestDist),
    Total is Dist + RestDist.

sort_paths(Paths, Sorted) :-
    map_list_to_pairs(path_cost, Paths, Paired),
    keysort(Paired, SortedPairs),
    pairs_values(SortedPairs, Sorted).

path_cost([H|T], Cost) :-
    reverse([H|T], Path),
    calculate_distance(Path, Cost).

% BFS Implementation
bfs_path(Start, End, Path) :-
    bfs_search([[Start]], End, Path).

bfs_search([[End|Path]|_], End, FinalPath) :-
    reverse([End|Path], FinalPath).

bfs_search([[Node|Path]|Queue], End, FinalPath) :-
    findall([Next, Node|Path],
            (road(Node, Next, _, _, open),
             \\+ member(Next, [Node|Path])),
            Extensions),
    append(Queue, Extensions, NewQueue),
    bfs_search(NewQueue, End, FinalPath).

% DFS Implementation
dfs_path(Start, End, Path) :-
    dfs_search([Start], End, Path).

dfs_search([End|Path], End, FinalPath) :-
    reverse([End|Path], FinalPath).

dfs_search([Node|Path], End, FinalPath) :-
    road(Node, Next, _, _, open),
    \\+ member(Next, [Node|Path]),
    dfs_search([Next, Node|Path], End, FinalPath).

% Fastest route (considering road type speeds)
fastest_path(Start, End, Path, TotalTime) :-
    dijkstra_time([[Start, 0]], End, Path, TotalTime).

dijkstra_time([[End, Time]|_], End, [End], Time).

dijkstra_time([[Node, CurrentTime]|Queue], End, [Node|RestPath], TotalTime) :-
    findall([Next, NewTime],
            (travel_time(Node, Next, TravelTime),
             NewTime is CurrentTime + TravelTime),
            Extensions),
    append(Queue, Extensions, NewQueue),
    sort(2, @=<, NewQueue, SortedQueue),
    member([Next, NextTime], SortedQueue),
    dijkstra_time(SortedQueue, End, RestPath, RestTime),
    RestPath = [Next|_],
    TotalTime is RestTime.

% Path avoiding unpaved roads
paved_path(Start, End, Path, Distance) :-
    paved_dijkstra([[Start]], End, Path, Distance).

paved_dijkstra([[End|Path]|_], End, FinalPath, Distance) :-
    reverse([End|Path], FinalPath),
    calculate_distance(FinalPath, Distance).

paved_dijkstra([Current|Queue], End, Path, Distance) :-
    Current = [Node|_],
    findall([Next, Node|Current],
            (road(Node, Next, _, paved, open),
             \\+ member(Next, Current)),
            Extensions),
    append(Queue, Extensions, NewQueue),
    sort_paths(NewQueue, SortedQueue),
    paved_dijkstra(SortedQueue, End, Path, Distance).

% Path avoiding specific conditions
safe_path(Start, End, AvoidCondition, Path, Distance) :-
    safe_dijkstra([[Start]], End, AvoidCondition, Path, Distance).

safe_dijkstra([[End|Path]|_], End, _, FinalPath, Distance) :-
    reverse([End|Path], FinalPath),
    calculate_distance(FinalPath, Distance).

safe_dijkstra([Current|Queue], End, AvoidCondition, Path, Distance) :-
    Current = [Node|_],
    findall([Next, Node|Current],
            (road(Node, Next, _, _, open),
             \\+ road_condition(Node, Next, AvoidCondition),
             \\+ member(Next, Current)),
            Extensions),
    append(Queue, Extensions, NewQueue),
    sort_paths(NewQueue, SortedQueue),
    safe_dijkstra(SortedQueue, End, AvoidCondition, Path, Distance).
"""
        with open(self.prolog_file, 'w') as f:
            f.write(default_data)
        self.prolog.consult(self.prolog_file)
        print("✓ Created default network with sample Jamaican locations")
    
    def get_all_locations(self) -> List[str]:
        """Retrieve all unique locations from the network."""
        locations = set()
        try:
            # Query all locations with timeout protection
            query = "location(L)"
            for solution in self.prolog.query(query):
                if 'L' in solution:
                    # Convert to string if it's an atom
                    loc = str(solution['L'])
                    locations.add(loc)
        except KeyboardInterrupt:
            print("Query interrupted by user")
            raise
        except Exception as e:
            print(f"Error retrieving locations: {e}")
            # Try alternative method if location/1 fails
            try:
                print("Trying alternative method to get locations...")
                for solution in self.prolog.query("road(A, _, _, _, _)"):
                    if 'A' in solution:
                        locations.add(str(solution['A']))
                for solution in self.prolog.query("road(_, B, _, _, _)"):
                    if 'B' in solution:
                        locations.add(str(solution['B']))
            except Exception as e2:
                print(f"Alternative method also failed: {e2}")
        
        return sorted(list(locations))
    
    def add_road(self, source: str, dest: str, distance: float, 
                 road_type: str, status: str) -> bool:
        """Add a new road to the network."""
        try:
            query = f"assertz(road({source}, {dest}, {distance}, {road_type}, {status}))"
            list(self.prolog.query(query))
            
            self._append_to_file(
                f"road({source}, {dest}, {distance}, {road_type}, {status}).\n"
            )
            print(f"✓ Added road: {source} → {dest} ({distance}km, {road_type}, {status})")
            return True
        except Exception as e:
            print(f"✗ Error adding road: {e}")
            return False
    
    def update_road_status(self, source: str, dest: str, new_status: str) -> bool:
        """Update the status of an existing road."""
        try:
            query = f"road({source}, {dest}, D, T, _)"
            results = list(self.prolog.query(query))
            
            if not results:
                print(f"✗ Road not found: {source} → {dest}")
                return False
            
            distance = results[0]['D']
            road_type = results[0]['T']
            
            retract_query = f"retract(road({source}, {dest}, {distance}, {road_type}, _))"
            list(self.prolog.query(retract_query))
            
            assert_query = f"assertz(road({source}, {dest}, {distance}, {road_type}, {new_status}))"
            list(self.prolog.query(assert_query))
            
            print(f"✓ Updated road status: {source} → {dest} is now {new_status}")
            return True
        except Exception as e:
            print(f"✗ Error updating road: {e}")
            return False
    
    def add_road_condition(self, source: str, dest: str, condition: str) -> bool:
        """Add a road condition."""
        try:
            query = f"assertz(road_condition({source}, {dest}, {condition}))"
            list(self.prolog.query(query))
            
            self._append_to_file(
                f"road_condition({source}, {dest}, {condition}).\n"
            )
            print(f"✓ Added condition: {source} → {dest} has {condition}")
            return True
        except Exception as e:
            print(f"✗ Error adding condition: {e}")
            return False
    
    def find_path(self, start: str, end: str, criteria: str) -> Optional[Dict]:
        """Find a path between two locations based on specified criteria."""
        try:
            print(f"\n=== Finding path: {start} -> {end} (criteria: {criteria}) ===")
            
            if criteria == "shortest":
                query = f"shortest_path({start}, {end}, Path, Distance)"
                print(f"Query: {query}")
                results = list(self.prolog.query(query))
                print(f"Found {len(results)} paths")
                
                if results:
                    # Get the path with minimum distance
                    result = min(results, key=lambda x: x['Distance'])
                    path = result['Path']
                    distance = result['Distance']
                    time = self._calculate_time(path)
                    
                    return {
                        'path': path,
                        'distance': distance,
                        'time': time,
                        'criteria': 'Shortest Distance'
                    }
            
            elif criteria == "fastest":
                query = f"fastest_path({start}, {end}, Path, Time)"
                print(f"Query: {query}")
                results = list(self.prolog.query(query))
                print(f"Found {len(results)} paths")
                
                if results:
                    # Get the path with minimum time
                    result = min(results, key=lambda x: x['Time'])
                    path = result['Path']
                    time = result['Time']
                    distance = self._calculate_distance(path)
                    
                    return {
                        'path': path,
                        'distance': distance,
                        'time': time,
                        'criteria': 'Fastest Route'
                    }
            
            elif criteria == "paved":
                query = f"paved_path({start}, {end}, Path, Distance)"
                print(f"Query: {query}")
                results = list(self.prolog.query(query))
                print(f"Found {len(results)} paths")
                
                if results:
                    # Get the path with minimum distance
                    result = min(results, key=lambda x: x['Distance'])
                    path = result['Path']
                    distance = result['Distance']
                    time = self._calculate_time(path)
                    
                    return {
                        'path': path,
                        'distance': distance,
                        'time': time,
                        'criteria': 'Paved Roads Only'
                    }
            
            elif criteria in ["no_potholes", "no_cisterns"]:
                condition = "deep_potholes" if criteria == "no_potholes" else "broken_cisterns"
                query = f"safe_path({start}, {end}, {condition}, Path, Distance)"
                print(f"Query: {query}")
                results = list(self.prolog.query(query))
                print(f"Found {len(results)} paths")
                
                if results:
                    # Get the path with minimum distance
                    result = min(results, key=lambda x: x['Distance'])
                    path = result['Path']
                    distance = result['Distance']
                    time = self._calculate_time(path)
                    
                    return {
                        'path': path,
                        'distance': distance,
                        'time': time,
                        'criteria': f'Avoiding {condition.replace("_", " ").title()}'
                    }
            
            elif criteria == "bfs":
                query = f"bfs_path({start}, {end}, Path)"
                print(f"Query: {query}")
                results = list(self.prolog.query(query))
                print(f"Found {len(results)} paths")
                
                if results:
                    # BFS returns paths in order, take the first one (shortest hops)
                    path = results[0]['Path']
                    distance = self._calculate_distance(path)
                    time = self._calculate_time(path)
                    
                    return {
                        'path': path,
                        'distance': distance,
                        'time': time,
                        'criteria': 'BFS (Any Valid Path)'
                    }
            
            print("No path found - query returned no results")
            return None
            
        except Exception as e:
            print(f"✗ Error finding path: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_distance(self, path: List[str]) -> float:
        """Calculate total distance for a path."""
        total = 0
        for i in range(len(path) - 1):
            # Use connected predicate (matches new Prolog file)
            query = f"connected({path[i]}, {path[i+1]}, D, _, _)"
            results = list(self.prolog.query(query))
            if results:
                total += results[0]['D']
        return total
    
    def _calculate_time(self, path: List[str]) -> float:
        """Calculate estimated travel time in minutes."""
        total_time = 0
        for i in range(len(path) - 1):
            # Try travel_time predicate
            query = f"travel_time({path[i]}, {path[i+1]}, T)"
            results = list(self.prolog.query(query))
            if results:
                total_time += results[0]['T']
            else:
                # Fallback: calculate manually
                query = f"connected({path[i]}, {path[i+1]}, D, Type, _)"
                results = list(self.prolog.query(query))
                if results:
                    distance = results[0]['D']
                    road_type = results[0]['Type']
                    # Get speed for road type
                    speed_query = f"speed({road_type}, Speed)"
                    speed_results = list(self.prolog.query(speed_query))
                    if speed_results:
                        speed = speed_results[0]['Speed']
                        total_time += (distance / speed) * 60
        return total_time
    
    def _append_to_file(self, content: str):
        """Append content to the Prolog file."""
        with open(self.prolog_file, 'a') as f:
            f.write(content)


class RoadNetworkGUI:
    """
    Main GUI class for the Jamaican Road Network System.
    Provides user and administrator interfaces.
    """
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("🇯🇲 Jamaican Rural Road Network Pathfinding System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Initialize the network backend
        try:
            self.network = JamaicaRoadNetwork()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize network: {e}\n\nPlease ensure SWI-Prolog is installed.")
            self.root.destroy()
            return
        
        # Setup the GUI
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Configure ttk styles for consistent appearance."""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', 
                       font=('Arial', 18, 'bold'),
                       background='#2c3e50',
                       foreground='#ecf0f1')
        
        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       background='#34495e',
                       foreground='#ecf0f1',
                       padding=10)
        
        style.configure('Info.TLabel',
                       font=('Arial', 10),
                       background='#34495e',
                       foreground='#ecf0f1')
        
        style.configure('Custom.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.configure('Custom.TFrame',
                       background='#34495e')
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Initialize status variable FIRST before creating any tabs
        self.status_var = tk.StringVar(value="Ready - System initialized successfully!")
        
        main_container = ttk.Frame(self.root, style='Custom.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_label = ttk.Label(
            main_container,
            text="🇯🇲 Jamaican Rural Road Network System",
            style='Title.TLabel'
        )
        title_label.pack(pady=10)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.create_pathfinding_tab()
        self.create_admin_tab()
        self.create_network_info_tab()
        
        # Status bar at bottom
        status_bar = ttk.Label(
            main_container,
            textvariable=self.status_var,
            style='Info.TLabel',
            relief=tk.SUNKEN
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def create_pathfinding_tab(self):
        """Create the pathfinding interface tab."""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="🔍 Find Path")
        
        left_frame = ttk.LabelFrame(
            tab,
            text="Path Configuration",
            padding=15,
            style='Custom.TFrame'
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Starting Location:",
                 style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(
            left_frame,
            textvariable=self.start_var,
            state='readonly',
            width=30
        )
        self.start_combo.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Destination:",
                 style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.dest_var = tk.StringVar()
        self.dest_combo = ttk.Combobox(
            left_frame,
            textvariable=self.dest_var,
            state='readonly',
            width=30
        )
        self.dest_combo.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Path Criteria:",
                 style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.criteria_var = tk.StringVar(value="shortest")
        criteria_options = [
            ("Shortest Distance", "shortest"),
            ("Fastest Route", "fastest"),
            ("Paved Roads Only", "paved"),
            ("Avoid Deep Potholes", "no_potholes"),
            ("Avoid Broken Cisterns", "no_cisterns"),
            ("Any Valid Path (BFS)", "bfs")
        ]
        
        criteria_frame = ttk.Frame(left_frame, style='Custom.TFrame')
        criteria_frame.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        for i, (text, value) in enumerate(criteria_options):
            ttk.Radiobutton(
                criteria_frame,
                text=text,
                variable=self.criteria_var,
                value=value
            ).pack(anchor=tk.W, pady=2)
        
        find_btn = ttk.Button(
            left_frame,
            text="🔍 Find Path",
            command=self.find_path,
            style='Custom.TButton'
        )
        find_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        refresh_btn = ttk.Button(
            left_frame,
            text="🔄 Refresh Locations",
            command=self.refresh_locations,
            style='Custom.TButton'
        )
        refresh_btn.grid(row=4, column=0, columnspan=2, pady=5)
        
        right_frame = ttk.LabelFrame(
            tab,
            text="Path Results",
            padding=15,
            style='Custom.TFrame'
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=50,
            height=30,
            font=('Courier', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_locations()
        
    def create_admin_tab(self):
        """Create the administrator interface tab."""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="⚙️ Admin Panel")
        
        admin_notebook = ttk.Notebook(tab)
        admin_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_add_road_tab(admin_notebook)
        self.create_update_status_tab(admin_notebook)
        self.create_add_condition_tab(admin_notebook)
        
    def create_add_road_tab(self, parent):
        """Create the add road interface."""
        tab = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(tab, text="➕ Add Road")
        
        frame = ttk.LabelFrame(tab, text="New Road Information", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Source Location:",
                 style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.add_source_entry = ttk.Entry(frame, width=30)
        self.add_source_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Destination:",
                 style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.add_dest_entry = ttk.Entry(frame, width=30)
        self.add_dest_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Distance (km):",
                 style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.add_distance_entry = ttk.Entry(frame, width=30)
        self.add_distance_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Road Type:",
                 style='Info.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.add_type_var = tk.StringVar(value="paved")
        type_frame = ttk.Frame(frame, style='Custom.TFrame')
        type_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Radiobutton(type_frame, text="Paved", variable=self.add_type_var,
                       value="paved").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Unpaved", variable=self.add_type_var,
                       value="unpaved").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame, text="Status:",
                 style='Info.TLabel').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.add_status_var = tk.StringVar(value="open")
        status_frame = ttk.Frame(frame, style='Custom.TFrame')
        status_frame.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Radiobutton(status_frame, text="Open", variable=self.add_status_var,
                       value="open").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(status_frame, text="Closed", variable=self.add_status_var,
                       value="closed").pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(
            frame,
            text="➕ Add Road",
            command=self.add_road,
            style='Custom.TButton'
        )
        add_btn.grid(row=5, column=0, columnspan=2, pady=20)
        
    def create_update_status_tab(self, parent):
        """Create the update road status interface."""
        tab = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(tab, text="🔄 Update Status")
        
        frame = ttk.LabelFrame(tab, text="Update Road Status", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Source Location:",
                 style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.update_source_entry = ttk.Entry(frame, width=30)
        self.update_source_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Destination:",
                 style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.update_dest_entry = ttk.Entry(frame, width=30)
        self.update_dest_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="New Status:",
                 style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.update_status_var = tk.StringVar(value="open")
        status_frame = ttk.Frame(frame, style='Custom.TFrame')
        status_frame.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Radiobutton(status_frame, text="Open", variable=self.update_status_var,
                       value="open").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(status_frame, text="Closed", variable=self.update_status_var,
                       value="closed").pack(side=tk.LEFT, padx=5)
        
        update_btn = ttk.Button(
            frame,
            text="🔄 Update Status",
            command=self.update_road_status,
            style='Custom.TButton'
        )
        update_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
    def create_add_condition_tab(self, parent):
        """Create the add road condition interface."""
        tab = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(tab, text="⚠️ Add Condition")
        
        frame = ttk.LabelFrame(tab, text="Add Road Condition", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Source Location:",
                 style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cond_source_entry = ttk.Entry(frame, width=30)
        self.cond_source_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Destination:",
                 style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cond_dest_entry = ttk.Entry(frame, width=30)
        self.cond_dest_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Condition Type:",
                 style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.cond_type_var = tk.StringVar(value="deep_potholes")
        cond_frame = ttk.Frame(frame, style='Custom.TFrame')
        cond_frame.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Radiobutton(cond_frame, text="Deep Potholes",
                       variable=self.cond_type_var,
                       value="deep_potholes").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(cond_frame, text="Broken Cisterns",
                       variable=self.cond_type_var,
                       value="broken_cisterns").pack(anchor=tk.W, pady=2)
        
        add_btn = ttk.Button(
            frame,
            text="⚠️ Add Condition",
            command=self.add_condition,
            style='Custom.TButton'
        )
        add_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
    def create_network_info_tab(self):
        """Create the network information tab."""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="ℹ️ Network Info")
        
        info_frame = ttk.LabelFrame(tab, text="Network Statistics", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            wrap=tk.WORD,
            width=80,
            height=30,
            font=('Courier', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        refresh_btn = ttk.Button(
            info_frame,
            text="🔄 Refresh Information",
            command=self.display_network_info,
            style='Custom.TButton'
        )
        refresh_btn.pack(pady=10)
        
        self.display_network_info()
        
    def refresh_locations(self):
        """Refresh the list of available locations."""
        locations = self.network.get_all_locations()
        self.start_combo['values'] = locations
        self.dest_combo['values'] = locations
        
        if locations:
            self.start_combo.current(0)
            self.dest_combo.current(min(1, len(locations) - 1))
        
        self.status_var.set(f"Loaded {len(locations)} locations")
        
    def find_path(self):
        """Execute pathfinding based on user input."""
        start = self.start_var.get()
        dest = self.dest_var.get()
        criteria = self.criteria_var.get()
        
        if not start or not dest:
            messagebox.showwarning("Input Required", "Please select both start and destination")
            return
        
        if start == dest:
            messagebox.showwarning("Invalid Input", "Start and destination must be different")
            return
        
        self.status_var.set(f"Finding path from {start} to {dest}...")
        self.results_text.delete(1.0, tk.END)
        
        result = self.network.find_path(start, dest, criteria)
        
        if result:
            output = "="*60 + "\n"
            output += "PATH FOUND! ✓\n"
            output += "="*60 + "\n\n"
            output += f"Criteria: {result['criteria']}\n"
            output += f"From: {start}\n"
            output += f"To: {dest}\n\n"
            output += "-"*60 + "\n"
            output += "ROUTE:\n"
            output += "-"*60 + "\n"
            
            path_str = " → ".join(result['path'])
            output += f"\n{path_str}\n\n"
            
            output += "-"*60 + "\n"
            output += "SUMMARY:\n"
            output += "-"*60 + "\n"
            output += f"📏 Total Distance: {result['distance']:.2f} km\n"
            output += f"⏱️  Estimated Time: {result['time']:.2f} minutes\n"
            output += f"                  ({result['time']/60:.2f} hours)\n"
            output += f"🛣️  Number of Segments: {len(result['path']) - 1}\n"
            output += "="*60 + "\n"
            
            self.status_var.set("Path found successfully!")
        else:
            output = "="*60 + "\n"
            output += "NO PATH FOUND ✗\n"
            output += "="*60 + "\n\n"
            output += f"Could not find a route from {start} to {dest}\n"
            output += "with the specified criteria.\n\n"
            output += "Possible reasons:\n"
            output += "• No connecting roads exist\n"
            output += "• All routes are blocked/closed\n"
            output += "• Criteria too restrictive\n"
            output += "="*60 + "\n"
            
            self.status_var.set("No path found")
        
        self.results_text.insert(1.0, output)
        
    def add_road(self):
        """Add a new road to the network."""
        source = self.add_source_entry.get().strip().lower().replace(" ", "_")
        dest = self.add_dest_entry.get().strip().lower().replace(" ", "_")
        distance_str = self.add_distance_entry.get().strip()
        road_type = self.add_type_var.get()
        status = self.add_status_var.get()
        
        if not all([source, dest, distance_str]):
            messagebox.showwarning("Input Required", "Please fill in all fields")
            return
        
        try:
            distance = float(distance_str)
            if distance <= 0:
                raise ValueError("Distance must be positive")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Invalid distance: {e}")
            return
        
        success = self.network.add_road(source, dest, distance, road_type, status)
        
        if success:
            messagebox.showinfo("Success", f"Road added: {source} → {dest}")
            self.add_source_entry.delete(0, tk.END)
            self.add_dest_entry.delete(0, tk.END)
            self.add_distance_entry.delete(0, tk.END)
            self.refresh_locations()
            self.status_var.set("Road added successfully")
        else:
            messagebox.showerror("Error", "Failed to add road")
            
    def update_road_status(self):
        """Update the status of a road."""
        source = self.update_source_entry.get().strip().lower().replace(" ", "_")
        dest = self.update_dest_entry.get().strip().lower().replace(" ", "_")
        new_status = self.update_status_var.get()
        
        if not all([source, dest]):
            messagebox.showwarning("Input Required", "Please fill in all fields")
            return
        
        success = self.network.update_road_status(source, dest, new_status)
        
        if success:
            messagebox.showinfo("Success", f"Road status updated: {source} → {dest} is now {new_status}")
            self.update_source_entry.delete(0, tk.END)
            self.update_dest_entry.delete(0, tk.END)
            self.status_var.set("Road status updated")
        else:
            messagebox.showerror("Error", "Failed to update road status")
            
    def add_condition(self):
        """Add a road condition."""
        source = self.cond_source_entry.get().strip().lower().replace(" ", "_")
        dest = self.cond_dest_entry.get().strip().lower().replace(" ", "_")
        condition = self.cond_type_var.get()
        
        if not all([source, dest]):
            messagebox.showwarning("Input Required", "Please fill in all fields")
            return
        
        success = self.network.add_road_condition(source, dest, condition)
        
        if success:
            messagebox.showinfo("Success", f"Condition added: {source} → {dest} has {condition}")
            self.cond_source_entry.delete(0, tk.END)
            self.cond_dest_entry.delete(0, tk.END)
            self.status_var.set("Road condition added")
        else:
            messagebox.showerror("Error", "Failed to add condition")
            
    def display_network_info(self):
        """Display network statistics and information."""
        self.info_text.delete(1.0, tk.END)
        
        locations = self.network.get_all_locations()
        
        output = "="*70 + "\n"
        output += "JAMAICAN RURAL ROAD NETWORK - NETWORK INFORMATION\n"
        output += "="*70 + "\n\n"
        
        output += f"📍 Total Locations: {len(locations)}\n"
        output += "-"*70 + "\n"
        
        for i, loc in enumerate(locations, 1):
            output += f"  {i:2d}. {loc}\n"
        
        output += "\n"
        
        try:
            roads = list(self.network.prolog.query("road(A, B, D, T, S)"))
            unique_roads = set()
            for r in roads:
                road_tuple = tuple(sorted([r['A'], r['B']]))
                unique_roads.add(road_tuple)
            
            open_roads = [r for r in roads if r['S'] == 'open']
            closed_roads = [r for r in roads if r['S'] == 'closed']
            paved_roads = [r for r in roads if r['T'] == 'paved']
            unpaved_roads = [r for r in roads if r['T'] == 'unpaved']
            
            output += f"🛣️  Road Statistics:\n"
            output += "-"*70 + "\n"
            output += f"  Total Unique Roads: {len(unique_roads)}\n"
            output += f"  Total Directional Segments: {len(roads)}\n"
            output += f"  Open Roads: {len(open_roads)}\n"
            output += f"  Closed Roads: {len(closed_roads)}\n"
            output += f"  Paved Roads: {len(paved_roads)}\n"
            output += f"  Unpaved Roads: {len(unpaved_roads)}\n\n"
            
            output += "📋 All Roads:\n"
            output += "-"*70 + "\n"
            displayed_roads = set()
            for r in roads:
                road_key = tuple(sorted([r['A'], r['B']]))
                if road_key not in displayed_roads:
                    status_icon = "✓" if r['S'] == 'open' else "✗"
                    type_icon = "🛣️" if r['T'] == 'paved' else "🏞️"
                    output += f"  {status_icon} {type_icon} {r['A']} ↔ {r['B']}: "
                    output += f"{r['D']} km ({r['T']}, {r['S']})\n"
                    displayed_roads.add(road_key)
            
        except Exception as e:
            output += f"\nError retrieving road information: {e}\n"
        
        output += "\n" + "="*70 + "\n"
        
        self.info_text.insert(1.0, output)
        self.status_var.set("Network information refreshed")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    
    # Show splash screen with instructions
    splash_text = """
    🇯🇲 Jamaican Rural Road Network Pathfinding System
    
    Standalone GUI Application
    
    This application runs independently - no CLI needed!
    
    Requirements:
    • Python 3.8+
    • SWI-Prolog 8.0+
    • PySwip library
    
    Loading...
    """
    
    print(splash_text)
    print("="*60)
    
    try:
        app = RoadNetworkGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        messagebox.showerror(
            "Startup Error",
            f"Failed to start application:\n\n{e}\n\n"
            "Please ensure:\n"
            "1. SWI-Prolog is installed\n"
            "2. PySwip is installed (pip install pyswip)\n"
            "3. road_network.pl exists or can be created"
        )


if __name__ == "__main__":
    main()