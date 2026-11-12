## 1. [An OpenFlow-Based Elephant-Flow Monitoring and Scheduling Strategy in SDN](https://www.mdpi.com/2079-9292/14/13/2663)

* **Mechanizm detekcji i klasyfikacji:** Kontroler SDN aktywnie zbiera statystyki z tablic przepływów każdego przełącznika OpenFlow za pomocą komunikatów `OFPFlowStatsRequest` wywoływanych co 5 sekund. Autorzy wprowadzili dwuwymiarowy podział ruchu na cztery klasy zależne od czasu trwania transmisji oraz chwilowej przepustowości: *large elephant flow* (czas $> 30\text{ s}$ i przepustowość $> 5\text{ Mb/s}$ – jedyna kategoria kwalifikowana do przełączenia trasy), *medium-sized elephant flow* ($> 30\text{ s}$ oraz $2–5\text{ Mb/s}$), *small elephant flow* ($> 30\text{ s}$ oraz $< 2\text{ Mb/s}$) oraz *mouse flow* (czas $< 30\text{ s}$, niezależnie od prędkości).


* **Sterowanie ruchem i weryfikacja eksperymentalna:** W badaniach z użyciem emulatora Mininet oraz narzędzia `iperf` wykazano, że w tradycyjnej strukturze Fat-Tree protokół STP blokuje łącza nadmiarowe, co przy pojawieniu się *elephant flow* prowadzi do zatoru na pojedynczej ścieżce i spadku przepustowości niemal do $0\text{ Mb/s}$. Zastosowanie dwuwarstwowej topologii Leaf-Spine bez STP odblokowało równorzędne ścieżki (ECMP), stabilizując transfer na poziomie $8–9\text{ Mb/s}$ przy zerowej utracie pakietów na wąskim gardle $10\text{ Mb/s}$. Harmonogramowanie zrealizowano w zewnętrznym skrypcie `reroute.sh`, który po wykryciu *large elephant flow* usuwa dotychczasową trasę (`del-flow`) i instaluje reguły dla alternatywnej ścieżki (`path_n`) w pętli naprzemiennej (Round-Robin), aby zapobiec okupowaniu jednego kabla przez cały czas trwania transferu.


* **Wady i ograniczenia:**
  * Przełączanie ścieżek metodą Round-Robin nie weryfikuje bieżącego obciążenia trasy docelowej.


  * Występuje 30-sekundowa bezwładność detekcji, ponieważ na początku wszystkie strumienie traktowane są jako *mice flows*.


  * Gwałtowne kasowanie wpisów i podmienianie portów wyjściowych w środku trwającej transmisji grozi rozsynchronizowaniem pakietów TCP.


  * Odpytywanie wszystkich przełączników co 5 sekund generuje wysoki narzut w płaszczyźnie sterowania.


  * Równoważenie obciążenia wykonywane jest wyłącznie w relacji host-host, bez uwzględnienia obciążenia serwerów docelowych.





---

## 2. [SDN based load balancing mechanism for elephant flow in data center networks](https://ieeexplore.ieee.org/document/7014867)

* **Problem badawczy i detekcja na hoście:** Autorzy wskazali, że statyczne haszowanie ECMP sprawdza się jedynie przy dużej liczbie drobnych sesji, natomiast w obecności *elephant flows* (stanowiących poniżej 10% sesji, ale generujących ponad 80% wolumenu danych) prowadzi do kolizji strumieni na wspólnych łączach i degradacji QoS. Detekcję przeniesiono do systemów operacyjnych maszyn końcowych poprzez warstwę pośrednią (*shim layer*) monitorującą bufory gniazd TCP, która po przekroczeniu progu liczby bajtów w oknie czasowym oznacza pakiety jako *elephant flows* (ruch mysi pozostaje obsługiwany przez domyślny ECMP).


* **Wyliczanie wag i ochrona kolejności pakietów TCP:** Kontroler cyklicznie odkrywa topologię sieci za pomocą pakietów LLDP oraz w stałych interwałach odpytuje przełączniki o liczniki portów w celu wyznaczenia bieżącego wykorzystania łączy. Następnie oblicza średnie obciążenie ścieżek kandydujących, wyklucza trasy silnie przeciążone i wyznacza wagi proporcjonalne do dostępnego pasma, wgrywając je sprzętowo do tablic grupowych OpenFlow. W celu ochrony sesji TCP przed rozsynchronizowaniem pakietów mierzona jest różnica czasu nadejścia kolejnych pakietów przepływu – jeżeli jest ona mniejsza od predefiniowanego progu, ruch trzyma się ściśle dotychczasowej ścieżki, a przełączenie na trasę alternatywną następuje wyłącznie podczas naturalnych przerw w transmisji.


* **Wady i ograniczenia:**
  * Detekcja oparta na warstwie pośredniej w buforach TCP wymaga inwazyjnej ingerencji w oprogramowanie systemowe każdego hosta końcowego.


  * Algorytm wykazuje niestabilność matematyczną zarówno przy niemal zerowym ruchu na łączach, jak i w sytuacji równomiernego nasycenia wszystkich ścieżek na poziomie 90%.


  * Periodyczne pobieranie statystyk ze wszystkich przełączników wprowadza stały narzut na kanał sterowania.


  * Decyzje routingowe nie uwzględniają bieżącego obciążenia serwerów końcowych.





---

## 3. [Elephant flow detection in datacenters using OpenFlow-based Hierarchical Statistics Pulling](https://ieeexplore.ieee.org/document/7037145)

* **Problem badawczy i zasada działania HSP:** Autorzy podjęli problem narzutu komunikacyjnego i obliczeniowego towarzyszącego metodzie indywidualnego odpytywania (ISP – *Individual Statistics Pulling*), w której pobieranie statystyk wszystkich przepływów w celu wykrycia zaledwie 1% *elephant flows* oznacza marnotrawienie 99% pakietów telemetrycznych. Zaproponowano mechanizm *Hierarchical Statistics Pulling* (HSP), oparty na standardowych komunikatach OpenFlow bez modyfikacji hostów ani przełączników. Kontroler modeluje przestrzeń adresową ($IP_{src} \times IP_{dst}$) jako obszar dwuwymiarowy i wysyła zwięzłe zapytania zagregowane (`Aggregate Stats Request`). Jeśli zsumowany licznik bajtów w badanym bloku przekracza próg (np. 100 MB), obszar jest dzielony na 4 równe ćwiartki, a procedura powtarzana jest przez zadaną liczbę rund (`Depth`, np. 4). Dopiero po osiągnięciu docelowej głębokości kontroler wysyła kosztowne zapytania indywidualne wyłącznie dla tych miniaturowych bloków, które nadal przekraczają próg.


* **Rozszerzenie ESHSP i weryfikacja:** W ulepszonej wersji *Elephant Sensitive HSP* (ESHSP) dodano pamięć podręczną *Elephant Store* (przechowującą 5-tuple znanych *elephant flows* w celu odejmowania ich wolumenu od odpowiedzi zagregowanych w kolejnych cyklach) oraz mechanizm *Range Splitting* (trwałe dzielenie bloków o wysokiej koncentracji ruchu na mniejsze podobszary tworzące zbiór startowy *Initial Block*). Emulacje przeprowadzone w Mininecie z kontrolerem NOX dla topologii Fat-Tree oraz VL2 wykazały, że ESHSP redukuje zużycie pasma komunikatów kontrolnych o 70–86% oraz skraca czas detekcji o 66–93% względem metody ISP.


* **Wady i ograniczenia:**
  * Rekurencyjny podział przestrzeni na kilka poziomów wymaga wykonania sekwencji wielu zapytań i odpowiedzi, co generuje narzut czasu RTT kanału sterowania.


  * Mechanizm opiera się na sztywnym progu wolumenu (100 MB w 5-sekundowym oknie) bez analizy chwilowej dynamiki przyrostu przepustowości.


  * Rozwiązanie wykazuje wrażliwość na hierarchiczny schemat adresacji IP (w podsieciach Fat-Tree ruch skupia się nierównomiernie w wybranych blokach).


  * Praca ogranicza się wyłącznie do samej detekcji *elephant flows* i nie definiuje algorytmu trasowania ani ochrony pakietów TCP przed zmianą kolejności.