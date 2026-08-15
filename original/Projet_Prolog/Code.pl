:- use_module(library(random)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% first_n_elements(khawa_khawa, Count, List, PrefixElements)
%
% Extracts the first Count elements of List (i.e. its prefix)
% and returns them in PrefixElements.
%
% Parameters:
%   khawa_khawa   - Extra context parameter (as required by the project).
%   Count         - The number of leading elements to extract.
%   List          - The input list from which to extract elements.
%   PrefixElements- The resulting list containing the first Count elements.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_first_n_elements(khawa_khawa, 0, _List, []) :- !.
khawa_khawa_first_n_elements(khawa_khawa, _Count, [], []) :- !.
khawa_khawa_first_n_elements(khawa_khawa, Count, [Head|Tail], [Head|Rest]) :-
    Count > 0,
    Count1 is Count - 1,
    khawa_khawa_first_n_elements(khawa_khawa, Count1, Tail, Rest).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% select_weighted(khawa_khawa, Probabilities, Elements, ChosenElement)
%
% Selects one element from Elements according to the provided probability
% distribution in Probabilities. A random value is generated and the helper
% predicate select_by_prob/5 is used to determine the chosen element.
%
% Parameters:
%   khawa_khawa   - Extra context parameter.
%   Probabilities - List of probabilities for each element.
%   Elements      - List of candidate elements.
%   ChosenElement - The element selected based on the distribution.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_select_weighted(khawa_khawa, Probabilities, Elements, ChosenElement) :-
    random(RandomValue),
    khawa_khawa_select_by_prob(khawa_khawa, Probabilities, Elements, RandomValue, ChosenElement).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% select_by_prob(khawa_khawa, Probabilities, Elements, Random, ChosenElement)
%
% Helper predicate that traverses the list of probabilities and elements.
% It subtracts the probability from the random value until a threshold is met.
%
% Parameters:
%   khawa_khawa   - Extra context parameter.
%   Probabilities - List of probabilities.
%   Elements      - List of candidate elements.
%   Random        - The current random value.
%   ChosenElement - The selected element when threshold is reached.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_select_by_prob(khawa_khawa, [Prob|_], [Elem|_], Random, Elem) :-
    Random =< Prob, !.
khawa_khawa_select_by_prob(khawa_khawa, [Prob|RestProbs], [_|RestElems], Random, ChosenElement) :-
    Random1 is Random - Prob,
    khawa_khawa_select_by_prob(khawa_khawa, RestProbs, RestElems, Random1, ChosenElement).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% second_elements(khawa_khawa, ListOfPairs, Seconds)
%
% From a list where each element is a pair (or list with at least 2 elements),
% extracts the second element from each pair.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   ListOfPairs - A list of sublists (each representing a pair).
%   Seconds     - Resulting list of the second elements.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_second_elements(khawa_khawa, [], []).
khawa_khawa_second_elements(khawa_khawa, [[_, Second|_]|RestPairs], [Second|Seconds]) :-
   khawa_khawa_second_elements(khawa_khawa, RestPairs, Seconds).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% count_elem(khawa_khawa, Element, List, Count)
%
% Counts the number of times Element occurs in List.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   Element     - The element to count.
%   List        - The list in which to count occurrences.
%   Count       - The resulting count.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_count_elem(khawa_khawa, _Element, [], 0).
khawa_khawa_count_elem(khawa_khawa, Element, [Element|Rest], Count) :-
    khawa_khawa_count_elem(khawa_khawa, Element, Rest, Count1),
    Count is Count1 + 1.
khawa_khawa_count_elem(khawa_khawa, Element, [_|Rest], Count) :-
    khawa_khawa_count_elem(khawa_khawa, Element, Rest, Count).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% rel_freq_stats(khawa_khawa, BigList, QueryList, Stats)
%
% Computes relative frequency statistics for each element in QueryList based on
% its occurrence in BigList. For each element, it calculates both the frequency
% and a variance term.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   BigList     - The list in which frequencies are computed.
%   QueryList   - The list of elements for which the stats are wanted.
%   Stats       - A list of triples: [Element, Frequency, VarianceTerm].
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_rel_freq_stats(khawa_khawa, BigList, QueryList, Stats) :-
    length(BigList, Total),
    khawa_khawa_rel_freq_stats_internal(khawa_khawa, QueryList, BigList, Total, Stats).

% Helper predicate for rel_freq_stats/4.
khawa_khawa_rel_freq_stats_internal(khawa_khawa, [], _BigList, _Total, []).
khawa_khawa_rel_freq_stats_internal(khawa_khawa, [Element|RestQueries], BigList, Total, [[Element, Frequency, VarianceTerm]|StatsRest]) :-
    khawa_khawa_count_elem(khawa_khawa, Element, BigList, Count),
    ( Total =:= 0 -> Frequency = 0 ; Frequency is Count / Total ),
    ( Total =:= 0 -> VarianceTerm = 0 ; VarianceTerm is Frequency * (1 - Frequency) / Total ),
    khawa_khawa_rel_freq_stats_internal(khawa_khawa, RestQueries, BigList, Total, StatsRest).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% normal_pdf(khawa_khawa, X, PdfValue)
%
% Computes the value of the standard normal probability density function at X.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   X           - The point at which to evaluate the PDF.
%   PdfValue    - The resulting probability density.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_normal_pdf(khawa_khawa, X, PdfValue) :-
    PdfValue is 1 / sqrt(2 * 3.141592653589793) * exp(-X * X / 2).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% normal_area(khawa_khawa, A, B, NumIntervals, Area)
%
% Approximates the area under the standard normal curve between A and B using
% a Riemann sum with NumIntervals subintervals.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   A, B        - The interval limits.
%   NumIntervals- Number of subintervals to use.
%   Area        - The approximate area under the curve.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_normal_area(khawa_khawa, A, B, NumIntervals, Area) :-
    Delta is (B - A) / NumIntervals,
    khawa_khawa_normal_area_helper(khawa_khawa, A, Delta, NumIntervals, 0, Area).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% normal_area_helper(khawa_khawa, CurrentX, Delta, NumIntervals, Accumulated, Area)
%
% Helper predicate to recursively compute the Riemann sum for normal_area/5.
%
% Parameters:
%   khawa_khawa  - Extra context parameter.
%   CurrentX     - The beginning of the current subinterval.
%   Delta        - Width of each subinterval.
%   NumIntervals - Remaining number of subintervals.
%   Accumulated  - Accumulated area so far.
%   Area         - Final computed area.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_normal_area_helper(khawa_khawa, _CurrentX, _Delta, 0, Accumulated, Accumulated).
khawa_khawa_normal_area_helper(khawa_khawa, CurrentX, Delta, NumIntervals, Accumulated, Area) :-
    NumIntervals > 0,
    Mid is CurrentX + Delta / 2,  % Midpoint of current subinterval
    khawa_khawa_normal_pdf(khawa_khawa, Mid, Y),
    NewAccumulated is Accumulated + Y * Delta,
    NextX is CurrentX + Delta,
    NextIntervals is NumIntervals - 1,
    khawa_khawa_normal_area_helper(khawa_khawa, NextX, Delta, NextIntervals, NewAccumulated, Area).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% distance_test(khawa_khawa, Variance, Result)
%
% Based on a given Variance, calculates a probability result using the normal_area
% approximation. If Variance is 0 the result is 1.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   Variance    - The variance value.
%   Result      - The resulting probability.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_distance_test(khawa_khawa, 0, 1).  % Special case: zero variance yields probability 1.
khawa_khawa_distance_test(khawa_khawa, Variance, Result) :-
    Bound is 0.1 / sqrt(Variance),
    khawa_khawa_normal_area(khawa_khawa, -Bound, Bound, 1000, Result).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% proba_of_strategy(khawa_khawa, StrategyList, Probabilities)
%
% Computes probabilities for each strategy defined in StrategyList. Each strategy is
% a triple [Element, Frequency, VarianceTerm]. The resulting list Probabilities holds
% the probability value obtained from distance_test for each strategy.
%
% Parameters:
%   khawa_khawa  - Extra context parameter.
%   StrategyList - List of strategies as triples.
%   Probabilities- List of computed probability values.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_proba_of_strategy(khawa_khawa, [], []).
khawa_khawa_proba_of_strategy(khawa_khawa, [[_, _, Variance]|RestStrategies], [Probability|RestProbabilities]) :-
    khawa_khawa_distance_test(khawa_khawa, Variance, Probability),
    khawa_khawa_proba_of_strategy(khawa_khawa, RestStrategies, RestProbabilities).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% matrix_A(khawa_khawa, MatrixA)
%
% Provides the constant matrix A used for computing the best
% response(Matrice de gain).
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   MatrixA     - The constant matrix used in response calculations.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_matrix_A(khawa_khawa, [
    [1, 0, 3, 4, 5],
    [3, 2, 0, 4, 5],
    [1, 5, 3, 0, 5],
    [1, 2, 7, 4, 0],
    [1, 2, 3, 9, 5]
]).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% best_response(khawa_khawa, StrategyVector, MatrixA, Response)
%
% Determines the best response given a strategy vector and matrix A. This is done by
% transposing the matrix, computing dot products with the strategy vector, selecting the
% index of the maximum dot product, and constructing a one-hot response vector.
%
% Parameters:
%   khawa_khawa   - Extra context parameter.
%   StrategyVector- The vector representing the weighted strategy.
%   MatrixA       - The constant matrix A.
%   Response      - The generated response vector (one-hot encoded).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_best_response(khawa_khawa, StrategyVector, MatrixA, Response) :-
    khawa_khawa_transpose(khawa_khawa, MatrixA, TransposedA),
    maplist(khawa_khawa_dot_product_with_context(khawa_khawa, StrategyVector), TransposedA, DotProducts),
    khawa_khawa_max_index(khawa_khawa, DotProducts, MaxIndex),
    length(DotProducts, Length),
    khawa_khawa_zeros(khawa_khawa, Length, ZeroVector),
    khawa_khawa_set_at_index(khawa_khawa, ZeroVector, MaxIndex, 1, Response).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% dot_product(khawa_khawa, Vector1, Vector2, Product)
%
% Computes the dot product of two numeric vectors.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   Vector1     - The first vector.
%   Vector2     - The second vector.
%   Product     - The resulting dot product.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_dot_product(khawa_khawa, [], [], 0).
khawa_khawa_dot_product(khawa_khawa, [X|Xs], [Y|Ys], Product) :-
    khawa_khawa_dot_product(khawa_khawa, Xs, Ys, PartialProduct),
    Product is X * Y + PartialProduct.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% dot_product_with_context(khawa_khawa, FixedVector, OtherVector, Product)
%
% Wrapper predicate used with maplist to compute the dot product between a fixed vector
% and each vector in a list.
%
% Parameters:
%   khawa_khawa  - Extra context parameter.
%   FixedVector  - The fixed vector used in every dot product.
%   OtherVector  - A vector from the list.
%   Product      - The computed dot product.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_dot_product_with_context(khawa_khawa, FixedVector, OtherVector, Product) :-
    khawa_khawa_dot_product(khawa_khawa, FixedVector, OtherVector, Product).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% transpose(khawa_khawa, Matrix, Transposed)
%
% Transposes a matrix.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   Matrix      - The input matrix (list of lists).
%   Transposed  - The resulting transposed matrix.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_transpose(khawa_khawa, [], []).
khawa_khawa_transpose(khawa_khawa, [[]|_], []).
khawa_khawa_transpose(khawa_khawa, Matrix, [Row|Rows]) :-
    maplist(khawa_khawa_list_head(khawa_khawa), Matrix, Row),
    maplist(khawa_khawa_list_tail(khawa_khawa), Matrix, RestMatrix),
    khawa_khawa_transpose(khawa_khawa, RestMatrix, Rows).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% list_head(khawa_khawa, List, Head)
%
% Retrieves the first element of List.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   List        - The input list.
%   Head        - The head (first element) of the list.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_list_head(khawa_khawa, [Head|_], Head).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% list_tail(khawa_khawa, List, Tail)
%
% Retrieves the tail (all elements after the head) of List.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   List        - The input list.
%   Tail        - The resulting tail of the list.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_list_tail(khawa_khawa, [_|Tail], Tail).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% max_index(khawa_khawa, List, MaxIndex)
%
% Finds the index of the maximum element within List.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   List        - The list of numbers.
%   MaxIndex    - The index (0-based) of the maximum value in List.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_max_index(khawa_khawa, [First|Rest], MaxIndex) :-
    khawa_khawa_max_index_helper(khawa_khawa, Rest, First, 0, 0, MaxIndex).

% Helper predicate for max_index/3.
khawa_khawa_max_index_helper(khawa_khawa, [], _CurrentMax, _CurrentPos, MaxIndex, MaxIndex).
khawa_khawa_max_index_helper(khawa_khawa, [H|T], CurrentMax, CurrentPos, CurrentMaxIndex, MaxIndex) :-
    NewPos is CurrentPos + 1,
    ( H > CurrentMax ->
        NewMax = H,
        NewMaxIndex = NewPos
    ;
        NewMax = CurrentMax,
        NewMaxIndex = CurrentMaxIndex
    ),
    khawa_khawa_max_index_helper(khawa_khawa, T, NewMax, NewPos, NewMaxIndex, MaxIndex).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% zeros(khawa_khawa, Length, ZeroList)
%
% Creates a list of Length zeros.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   Length      - The desired length of the zero list.
%   ZeroList    - The resulting list filled with zeros.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_zeros(khawa_khawa, 0, []).
khawa_khawa_zeros(khawa_khawa, N, [0|Rest]) :-
    N > 0,
    N1 is N - 1,
    khawa_khawa_zeros(khawa_khawa, N1, Rest).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% set_at_index(khawa_khawa, List, Index, Value, NewList)
%
% Sets the element at the specified Index in List to Value,
% producing the modified NewList.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   List        - The original list.
%   Index       - The 0-based index to update.
%   Value       - The value to place at the specified index.
%   NewList     - The modified list after updating.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_set_at_index(khawa_khawa, [_|Tail], 0, Value, [Value|Tail]).
khawa_khawa_set_at_index(khawa_khawa, [Head|Tail], Index, Value, [Head|NewTail]) :-
    Index > 0,
    Index1 is Index - 1,
    khawa_khawa_set_at_index(khawa_khawa, Tail, Index1, Value, NewTail).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% update(khawa_khawa, List0, List1, List2, ResultList)
%
% Updates List0 using List1 and List2 with the formula:
%   Result = Element_from_List0 + Element_from_List1 * (Element_from_List2 - Element_from_List0)
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   List0       - The original list.
%   List1       - The list of scaling factors.
%   List2       - The target list.
%   ResultList  - The resulting updated list.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_update(khawa_khawa, [], [], [], []).
khawa_khawa_update(khawa_khawa, [X0|Rest0], [X1|Rest1], [X2|Rest2], [R|ResultRest]) :-
    R is X0 + X1 * (X2 - X0),
    khawa_khawa_update(khawa_khawa, Rest0, Rest1, Rest2, ResultRest).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% product(khawa_khawa, List, Product)
%
% Computes the product of all elements in List.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   List        - The list of numbers.
%   Product     - The resulting product.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_product(khawa_khawa, [], 1).
khawa_khawa_product(khawa_khawa, [X|Xs], Product) :-
    khawa_khawa_product(khawa_khawa, Xs, PartialProduct),
    Product is X * PartialProduct.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% pairwise_multiply(khawa_khawa, List1, List2, ResultList)
%
% Performs element-wise multiplication of two lists, List1 and List2.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   List1       - The first list of numbers.
%   List2       - The second list of numbers.
%   ResultList  - The resulting list where each element is the product of the
%                 corresponding elements in List1 and List2.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_pairwise_multiply(khawa_khawa, [], [], []).
khawa_khawa_pairwise_multiply(khawa_khawa, [A|As], [B|Bs], [Product|Rest]) :-
    Product is A * B,
    khawa_khawa_pairwise_multiply(khawa_khawa, As, Bs, Rest).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% create_list(khawa_khawa, N, Value, List)
%
% Creates a list of length N where every element is the given Value.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   N           - Desired length of the list.
%   Value       - The value to fill the list with.
%   List        - The resulting list.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
khawa_khawa_create_list(khawa_khawa, 0, _Value, []).
khawa_khawa_create_list(khawa_khawa, N, Value, [Value|Rest]) :-
    N > 0,
    N1 is N - 1,
    khawa_khawa_create_list(khawa_khawa, N1, Value, Rest).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% play(khawa_khawa, GameHistory, Move)
%
% Main predicate that decides on the next move based on the GameHistory.
% Two strategies are implemented:
%   1. If fewer than 30 moves have occurred, choose a move at random using a fixed
%      probability distribution.
%   2. Otherwise, analyze the history to compute opponent move frequencies, determine
%      an optimal response through several computations (including best response and update),
%      and finally select a move based on the updated probabilities.
%
% Parameters:
%   khawa_khawa - Extra context parameter.
%   GameHistory - The list of past moves (each move is a [YourMove, OpponentMove] pair).
%   Move        - The chosen move (an integer between 1 and 5).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
joue(khawa_khawa, GameHistory, Move) :-
    length(GameHistory, Length),
    Length < 4,
    khawa_khawa_select_weighted(khawa_khawa, [0.03, 0.444, 0.203, 0.323, 0.0], [1,2,3,4,5], Move).

joue(khawa_khawa, GameHistory, Move) :-
     khawa_khawa_first_n_elements(khawa_khawa, 4, GameHistory, LastMoves),
    khawa_khawa_second_elements(khawa_khawa, LastMoves, OpponentMoves),
    khawa_khawa_rel_freq_stats(khawa_khawa, OpponentMoves, [1,2,3,4,5], Strategy),
   khawa_khawa_proba_of_strategy(khawa_khawa, Strategy, Probabilities),
    khawa_khawa_matrix_A(khawa_khawa, MatrixA),
    khawa_khawa_second_elements(khawa_khawa, Strategy, ExpectedStrategy),
    khawa_khawa_pairwise_multiply(khawa_khawa, ExpectedStrategy, Probabilities, WeightedStrategy),
    khawa_khawa_product(khawa_khawa, Probabilities, ProbaOfSuccess),
    khawa_khawa_create_list(khawa_khawa, 5, ProbaOfSuccess, ProbaOfSuccessVector),
    khawa_khawa_best_response(khawa_khawa, WeightedStrategy, MatrixA, Response),
    khawa_khawa_update(khawa_khawa, [0.03, 0.444, 0.203, 0.323, 0.0], ProbaOfSuccessVector, Response, Choice),
    khawa_khawa_select_weighted(khawa_khawa, Choice, [1,2,3,4,5], Move).







joue(nash_equilibrium, _, Coup) :-
    khawa_khawa_select_weighted(khawa_khawa,
                    [0,
                     0,
                     4/9,
                     2/9,
                     1/3], [1,2,3,4,5], Coup).









joue(stage_test, _, Coup) :-
    khawa_khawa_select_weighted(khawa_khawa,
        [0.03,
            0.444,
            0.203,
            0.323,
            0.0], [1,2,3,4,5], Coup).






:- discontiguous joue/3.
:- dynamic   param_khawa_khawa_prime/2.
:- dynamic   drapeau_fausse_repet/1.

%Paramètres réglables
param_khawa_khawa_prime(avance_sure , 15).
param_khawa_khawa_prime(retard_aggr , -20).
param_khawa_khawa_prime(repet_min   , 2).
param_khawa_khawa_prime(taux_nash   , 0.10).
param_khawa_khawa_prime(var_switch  , 0.25).

maj_param_cle(Cle, Val) :-
    retractall(param_khawa_khawa_prime(Cle,_)),
    assertz(param_khawa_khawa_prime(Cle,Val)).

%Boucle principale
joue(khawa_khawa_prime, Historique, Coup) :-
    parametres(AvanceOk, RetardMax, SeuilRep, TauxNash, VarSeuil),
    etat_score(Historique, Delta),
    repetition_adv(Historique, DernAdv, NbRep),
    variation_detectee(Historique, VarSeuil, Bascule),
    entropie_adv(Historique, H),
    est_titfortat(Historique, EstTFT),

    choisir_coup(Historique, Coup,               % sortie
                 AvanceOk, RetardMax, SeuilRep,  % paramètres
                 TauxNash,                       % taux Nash
                 Delta, DernAdv, NbRep,          % état score / répétition
                 Bascule, H, EstTFT).            % autres infos

% Sélection du coup  cascade de clauses
choisir_coup(_, Coup, _Av,_Rg,SeuilRep,_Tn,_Dlt,DernAdv,NbRep,_Bas,_H,_TFT) :-
    NbRep >= SeuilRep, !,
    Coup is ((DernAdv+4) mod 5)+1.                          % contre répétition

choisir_coup(_, Coup, AvanceOk,_Rg,_SRep,_Tn,Delta,DernAdv,_Nr,_Bas,_H,_TFT) :-
    Delta >= AvanceOk, !,
    coup_securise(DernAdv, Coup).                           % sécuriser avance

choisir_coup(_, Coup,_Av,_Rg,_SRep,Tn,_Dlt,_Da,_NbRep,true,_H,_TFT) :- !,
    coup_nash(Tn*2, Coup).                                  % adversaire instable

choisir_coup(_, Coup,_Av,_Rg,_SRep,Tn,_Dlt,_Da,_NbRep,false,H,_TFT) :-
    H > 1.8, !,
    coup_nash(Tn, Coup).                                    % jeu trop aléatoire

choisir_coup(Hist, Coup,_Av,RetardMax,_SRep,_Tn,Delta,_Da,_NbRep,false,_H,_TFT) :-
    Delta =< RetardMax, !,
    coup_agressif(Hist, Coup).                              % tenter piège

choisir_coup(_, Coup,_Av,_Rg,_SRep,_Tn,_Dlt,DernAdv,_NbRep,false,_H,true) :- !,
    casser_miroir(DernAdv, Coup).                           % casser TFT

choisir_coup(Hist, Coup, _Av,_Rg,_SRep,_Tn,_Dlt,_Da,_NbRep,_Bas,_H,_TFT) :-
    coup_adaptatif(Hist, Coup).                             % défaut

%Paramètres courants
parametres(Av,Rg,Rp,Tn,Sw) :-
    param_khawa_khawa_prime(avance_sure , Av),
    param_khawa_khawa_prime(retard_aggr , Rg),
    param_khawa_khawa_prime(repet_min   , Rp),
    param_khawa_khawa_prime(taux_nash   , Tn),
    param_khawa_khawa_prime(var_switch  , Sw).

%Score cumulé
etat_score(Hist, Delta) :-
    foldl(delta_tour, Hist, 0, Delta).

delta_tour([Moi,Adv], Acc, Suivant) :-
    ( abs(Moi-Adv)=:=1, Moi<Adv -> Suivant is Acc+1
    ; abs(Moi-Adv)=:=1, Moi>Adv -> Suivant is Acc-1
    ; Suivant = Acc).

% Répétitions adverses
repetition_adv([], _, 0).
repetition_adv([[_,Adv]|Reste], Adv, Nb) :-
    compte_rep(Adv, Reste, 1, Nb).

compte_rep(_, [], Acc, Acc).
compte_rep(X, [[_,X]|T], A, Nb) :-
    A1 is A+1, compte_rep(X,T,A1,Nb).
compte_rep(X, [[_,Y]|_], Nb, Nb) :- X=\=Y.

%Changement brutal
variation_detectee(Hist, Seuil, true) :-
    length(Hist,L), L>=10,
    prefixe(Hist,5,Recent),
    supprimer_prefixe(Hist,5,Reste),
    prefixe(Reste,5,Avant),
    distr_simple(Recent,D1),
    distr_simple(Avant ,D2),
    distance_L1(D1,D2,V),
    V > Seuil, !.
variation_detectee(_,_,false).

%Entropie locale
entropie_adv(Hist, H) :-
    prefixe(Hist,7,Fen),
    compte_coups(Fen,Comptes),
    total_compte(Comptes,Tot),
    ( Tot=:=0 -> H=0
    ; maplist(terme_shannon(Tot),Comptes,Ts),
      sum_list(Ts,S), H is -S).

terme_shannon(Tot,_-C,Term) :-
    ( C=:=0 -> Term=0
    ; P is C/Tot, Term is P*log(P)).

%Test tit-for-tatn
est_titfortat([[_,AdvAct],[MoiPrec,_]|_], true) :-
    AdvAct =:= MoiPrec, !.
est_titfortat(_, false).

%Coups spécialisés
coup_securise(3, Coup) :- random_member(Coup,[1,5]), !.
coup_securise(_, Coup) :- random_member(Coup,[2,4]).

coup_nash(Taux, Coup) :-
    random(R),
    ( R < Taux -> tirage_nash(Coup)
    ;             coup_adaptatif([],Coup)).

tirage_nash(Coup) :- random_member(Coup,[1,2,2,2,3,3,4,4,4,5]).

coup_agressif(_, Coup) :-
    drapeau_fausse_repet(done), !,
    coup_adaptatif([], Coup).
coup_agressif(_, Coup) :-
    random_member(Coup,[5,4]),
    assertz(drapeau_fausse_repet(done)).

casser_miroir(Adv, Coup) :-
    Tmp is (Adv+2) mod 5,
    (Tmp=:=0 -> Coup=5 ; Coup=Tmp).

%Stratégie adaptative
coup_adaptatif(Hist, Coup) :-
    distr_markov(Hist,3,Dm),
    distr_bayes(Hist,Db),
    distr_fenetre(Hist,0.9,Dh),
    melange([0.45,0.30,0.25],[Dm,Db,Dh],Dmix),
    meilleur_coup(Dmix,Coup).

%Distributions
distr_markov(Hist,N,Dist) :-
    prefixe(Hist,N,Fen),
    findall(A,member([_,A],Fen),Mvs),
    compte_coups(Mvs,Cs),
    total_compte(Cs,T),
    maplist(probabilite(T),Cs,Dist).

distr_bayes(Hist,Dist) :-
    compte_coups(Hist,Cs),
    total_compte(Cs,T),
    maplist(probabilite(T),Cs,Dist).

distr_fenetre(Hist,Lmb,Dist) :-
    hist_decroissant(Hist,Lmb,1.0,[],CoupsP),
    fusion_comptes(CoupsP,Cs),
    total_compte(Cs,T),
    maplist(probabilite(T),Cs,Dist).

hist_decroissant([],_,_,Acc,Acc).
hist_decroissant([[_,A]|T],L,W,Acc,Out) :-
    W1 is W*L,
    hist_decroissant(T,L,W1,[A-W|Acc],Out).

%Mélange linéaire
melange([W1,W2,W3],[D1,D2,D3],Mix) :-
    findall(M-P,(between(1,5,M),
                 membre(M,P1,D1), membre(M,P2,D2), membre(M,P3,D3),
                 P is W1*P1+W2*P2+W3*P3), Mix).

membre(M,P,Dist) :- member(M-P,Dist), !.
membre(_,0,_).

%Coup à meilleure espérance
meilleur_coup(Dist, Coup) :-
    findall(Esp-C,(between(1,5,C), esp_gain(C,Dist,Esp)),Lst),
    keysort(Lst,Tri), reverse(Tri,[_-Coup|_]).

esp_gain(Moi,Dist,Esp) :-
    findall(V,(member(Adv-P,Dist), gain(Moi,Adv,G), V is P*G),Ls),
    sum_list(Ls,Esp).

gain(Moi,Adv,G) :-
    Diff is abs(Moi-Adv),
    ( Diff=:=1, Moi<Adv -> G is Moi+Adv
    ; Diff=:=1           -> G = 0
    ;                       G = Moi).

%Comptage et probabilités
compte_coups(Liste,Comptes) :-
    findall(M-0,between(1,5,M),Init),
    foldl(compte_mvt, Liste, Init, Comptes).

compte_mvt([_,A],CsIn,CsOut) :- !, maj_compte(A,CsIn,CsOut).
compte_mvt(A,CsIn,CsOut)    :- maj_compte(A,CsIn,CsOut).

maj_compte(A,CsIn,CsOut) :-
    select(A-C, CsIn, Reste),
    C1 is C+1,
    CsOut = [A-C1|Reste].

total_compte(Cs,T) :- findall(C,member(_-C,Cs),Ls), sum_list(Ls,T).

probabilite(0,M-_,M-0) :- !.
probabilite(T,M-C,M-P) :- P is C/T.

% Fusion des comptes pondérés (A-Poids) vers table final
fusion_comptes(L,CsOut) :-
    findall(M-0,between(1,5,M),Init),
    foldl(ajout_poids, L, Init, CsOut).

ajout_poids(A-P, CsIn, CsOut) :-
    select(A-C, CsIn, Reste),
    C1 is C+P,
    CsOut = [A-C1|Reste].

prefixe(L,N,P) :- length(P,N), append(P,_,L).
supprimer_prefixe(L,N,R) :- length(P,N), append(P,R,L).

distr_simple(Extrait,D) :-
    compte_coups(Extrait,Cs), total_compte(Cs,T),
    maplist(probabilite(T),Cs,D).

distance_L1(D1,D2,V) :-
    findall(Diff,(member(M-P1,D1),member(M-P2,D2),Diff is abs(P1-P2)),Ds),
    sum_list(Ds,S), V is S/2.
 random_member(X,L) :- length(L,N), random_between(0,N-1,I), nth0(I,L,X).



