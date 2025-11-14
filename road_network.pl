% ============================================================================
% JAMAICAN RURAL ROAD NETWORK KNOWLEDGE BASE
% ============================================================================

:- dynamic road/5.
:- dynamic road_condition/3.

% ----------------------------------------------------------------------------
% FACTS: Road Network Data
% ----------------------------------------------------------------------------

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

% Road conditions
road_condition(port_morant, golden_grove, deep_potholes).
road_condition(morant_bay, yallahs, broken_cisterns).
road_condition(bath, stony_gut, deep_potholes).

% ----------------------------------------------------------------------------
% RULES: Make roads bidirectional
% ----------------------------------------------------------------------------

% Check if road exists in either direction
connected(A, B, Dist, Type, Status) :- road(A, B, Dist, Type, Status).
connected(A, B, Dist, Type, Status) :- road(B, A, Dist, Type, Status).

% Check if condition exists in either direction
has_condition(A, B, Condition) :- road_condition(A, B, Condition).
has_condition(A, B, Condition) :- road_condition(B, A, Condition).

% Get locations
location(L) :- road(L, _, _, _, _).
location(L) :- road(_, L, _, _, _).

% Speeds by road type
speed(paved, 60).
speed(unpaved, 30).

% Calculate travel time
travel_time(A, B, Time) :-
    connected(A, B, Distance, Type, open),
    speed(Type, Speed),
    Time is (Distance / Speed) * 60.

% ----------------------------------------------------------------------------
% ALGORITHM 1: BFS (Simplest - use this for testing)
% ----------------------------------------------------------------------------

bfs_path(Start, End, Path) :-
    bfs_queue([[Start]], End, Path).

bfs_queue([[End|Visited]|_], End, Path) :-
    reverse([End|Visited], Path).

bfs_queue([[Node|Visited]|Rest], End, Path) :-
    findall([Next, Node|Visited],
            (connected(Node, Next, _, _, open),
             \+ member(Next, [Node|Visited])),
            NewPaths),
    append(Rest, NewPaths, Queue),
    bfs_queue(Queue, End, Path).

% ----------------------------------------------------------------------------
% ALGORITHM 2: Shortest Path (Dijkstra-like)
% ----------------------------------------------------------------------------

shortest_path(Start, End, Path, Distance) :-
    bfs_path(Start, End, Path),
    path_distance(Path, Distance).

% Calculate total distance of a path
path_distance([_], 0).
path_distance([A,B|Rest], Total) :-
    connected(A, B, Dist, _, _),
    path_distance([B|Rest], RestDist),
    Total is Dist + RestDist.

% ----------------------------------------------------------------------------
% ALGORITHM 3: Fastest Path
% ----------------------------------------------------------------------------

fastest_path(Start, End, Path, Time) :-
    bfs_path(Start, End, Path),
    path_time(Path, Time).

% Calculate total time of a path
path_time([_], 0).
path_time([A,B|Rest], Total) :-
    travel_time(A, B, Time),
    path_time([B|Rest], RestTime),
    Total is Time + RestTime.

% ----------------------------------------------------------------------------
% ALGORITHM 4: Paved Roads Only
% ----------------------------------------------------------------------------

paved_path(Start, End, Path, Distance) :-
    paved_bfs([[Start]], End, Path),
    path_distance(Path, Distance).

paved_bfs([[End|Visited]|_], End, Path) :-
    reverse([End|Visited], Path).

paved_bfs([[Node|Visited]|Rest], End, Path) :-
    findall([Next, Node|Visited],
            (connected(Node, Next, _, paved, open),
             \+ member(Next, [Node|Visited])),
            NewPaths),
    append(Rest, NewPaths, Queue),
    paved_bfs(Queue, End, Path).

% ----------------------------------------------------------------------------
% ALGORITHM 5: Avoid Specific Conditions
% ----------------------------------------------------------------------------

safe_path(Start, End, AvoidCondition, Path, Distance) :-
    safe_bfs([[Start]], End, AvoidCondition, Path),
    path_distance(Path, Distance).

safe_bfs([[End|Visited]|_], End, _, Path) :-
    reverse([End|Visited], Path).

safe_bfs([[Node|Visited]|Rest], End, Condition, Path) :-
    findall([Next, Node|Visited],
            (connected(Node, Next, _, _, open),
             \+ has_condition(Node, Next, Condition),
             \+ member(Next, [Node|Visited])),
            NewPaths),
    append(Rest, NewPaths, Queue),
    safe_bfs(Queue, End, Condition, Path).

% ----------------------------------------------------------------------------
% ALGORITHM 6: DFS
% ----------------------------------------------------------------------------

dfs_path(Start, End, Path) :-
    dfs([Start], End, ReversePath),
    reverse(ReversePath, Path).

dfs([End|Visited], End, [End|Visited]).

dfs([Node|Visited], End, Path) :-
    connected(Node, Next, _, _, open),
    \+ member(Next, [Node|Visited]),
    dfs([Next, Node|Visited], End, Path).

% ============================================================================
% HELPER PREDICATES
% ============================================================================

% Get all roads (for display purposes)
all_roads(Roads) :-
    findall(road(A, B, D, T, S), road(A, B, D, T, S), Roads).

% Check if path exists
path_exists(Start, End) :-
    bfs_path(Start, End, _).

% ============================================================================
% END OF KNOWLEDGE BASE
% ============================================================================