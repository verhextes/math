import random
import math
import collections
import matplotlib.pyplot as plt

def generate_field(n=5, m=5): #создает поле n x m, расставляет цель и 3 ловушки
    cells = [(i, j) for i in range(n) for j in range(m)]
    start = (0, 0)
    available = [c for c in cells if c != start]
    
    goal = random.choice(available)
    available.remove(goal)
    
    traps = set()
    for _ in range(3):
        trap = random.choice(available)
        traps.add(trap)
        available.remove(trap)
        
    return n, m, start, goal, traps

def build_graph(n, m, traps):
    """Представляет поле как граф (список смежности)."""
    graph = {}
    for i in range(n):
        for j in range(m):
            if (i, j) in traps:
                continue
            
            neighbors = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < m and (ni, nj) not in traps:
                    neighbors.append((ni, nj))
            graph[(i, j)] = neighbors
    return graph

def bfs_shortest(graph, start, goal):
    """Ручная реализация поиска в ширину (BFS)."""
    if start == goal: return 0
    queue = collections.deque([(start, 0)])
    visited = {start}
    
    while queue:
        current, dist = queue.popleft()
        for neighbor in graph.get(current, []):
            if neighbor == goal:
                return dist + 1
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1

def single_random_walk(graph, start, goal, traps):
    """
    Один прогон случайного блуждания.
    Возвращает: (статус, количество_шагов, словарь_посещений)
    Статус: 1 - успех, 0 - провал (ловушка), -1 - тупик/лимит
    """
    current = start
    steps = 0
    visits = collections.defaultdict(int)
    visits[current] += 1
    
    max_steps = 10000 #защита от бесконечного блуждания
    
    while steps < max_steps: #если робот попал в ловушку
        if current in traps:
            return 0, steps, visits
            
        neighbors = graph.get(current, [])
        if not neighbors:
            return -1, steps, visits #окружен ловушками
        #выбираем случайного соседа
        current = random.choice(neighbors)
        steps += 1
        visits[current] += 1
        
        if current == goal:
            return 1, steps, visits
            
    return -1, steps, visits

def run_monte_carlo(graph, start, goal, traps, K=100000): #Запускает серию экспериментов и собирает статистику
    successful_steps = []
    failed_steps = []
    total_visits = collections.defaultdict(int)
    
    for _ in range(K):
        status, steps, visits = single_random_walk(graph, start, goal, traps)
        #собираем статистику посещений
        for cell, count in visits.items():
            total_visits[cell] += count
            
        if status == 1:
            successful_steps.append(steps)
        elif status == 0:
            failed_steps.append(steps)
            
    #расчет метрик
    success_rate = len(successful_steps) / K
    avg_steps = sum(successful_steps) / len(successful_steps) if successful_steps else 0
    avg_fail_steps = sum(failed_steps) / len(failed_steps) if failed_steps else 0
    
    #поиск моды посещений
    most_visited_cell = max(total_visits.items(), key=lambda x: x[1]) if total_visits else (None, 0)
    
    return {
        'success_rate': success_rate,
        'avg_steps': avg_steps,
        'avg_fail_steps': avg_fail_steps,
        'most_visited': most_visited_cell,
        'successful_steps_list': successful_steps
    }

def visualize_results(stats, shortest, n, m): #строит гистограмму распределения шагов
    plt.figure(figsize=(10, 6))
    
    #гистограмма успешных попыток
    plt.hist(stats['successful_steps_list'], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    
    #линия кратчайшего пути
    plt.axvline(x=shortest, color='red', linestyle='dashed', linewidth=2, 
                label=f'Кратчайший путь (BFS) = {shortest}')
    
    #линия мат ожидания
    plt.axvline(x=stats['avg_steps'], color='green', linestyle='dashed', linewidth=2, 
                label=f'Среднее (Монте-Карло) = {stats["avg_steps"]:.1f}')
    
    plt.title('Распределение количества шагов для успешных попыток')
    plt.xlabel('Количество шагов')
    plt.ylabel('Частота (количество симуляций)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

def print_heatmap(n, m, start, goal, traps, most_visited):
    #выводит текстовую тепловую карту в консоль
    print("\n          карта          ")
    print("S - старт, G - цель, T - ловушка, * - самая посещаемая клетка, . - обычная клетка")
    for i in range(n):
        row = ""
        for j in range(m):
            cell = (i, j)
            if cell == start: row += " S "
            elif cell == goal: row += " G "
            elif cell in traps: row += " T "
            elif cell == most_visited: row += " * "
            else: row += " . "
        print(row)
    print(f"самая посещаемая клетка: {most_visited}")

if __name__ == "__main__":
    N, M = 5, 5
    K_SIMULATIONS = 100000
    
    #генерация
    n, m, start, goal, traps = generate_field(N, M)
    print("     поле     ")
    print(f"размер: {n}x{m}")
    print(f"старт: {start}")
    print(f"цель: {goal}")
    print(f"ловушки: {traps}")
    
    #построение графа и BFS
    graph = build_graph(n, m, traps)
    shortest = bfs_shortest(graph, start, goal)
    print(f"\nкратчайший путь BFS: {shortest} шагов")
    
    if shortest == -1:
        print("цель недостижима из-за ловушек")
        exit()

    #симуляция Монте-Карло
    print(f"\nзапуск {K_SIMULATIONS} симуляций")
    stats = run_monte_carlo(graph, start, goal, traps, K=K_SIMULATIONS)
    
    #вывод статистики
    print("\n     результаты     ")
    print(f"вероятность успеха: {stats['success_rate'] * 100:.2f}%")
    print(f"мат ожидание шагов (успех): {stats['avg_steps']:.2f}")
    print(f"мат ожидание шагов (провал): {stats['avg_fail_steps']:.2f}")
    print(f"мода посещений: {stats['most_visited'][0]} (посещена {stats['most_visited'][1]} раз)")
    
    #cравнение
    print("\n      сравнение      ")
    if stats['avg_steps'] > 0:
        inefficiency = stats['avg_steps'] / shortest
        print(f"случайное блуждание в {inefficiency:.1f} раз(а) неэффективнее оптимального маршрута")
    
    #визуализация
    print_heatmap(n, m, start, goal, traps, stats['most_visited'][0])
    visualize_results(stats, shortest, n, m)
    
    #отчет
    print("\n   отчет     ")
    print(f"в ходе работы было смоделировано поле с препятствиями и целью \nС помощью BFS найден идеальный маршрут \nСимуляция Монте-Карло показала, что случайное блуждание крайне неэффективно: \nв среднем робот делает в {inefficiency:.1f} раз больше шагов, чем необходимо \nа вероятность успеха составляет всего {stats['success_rate']*100:.1f}% из-за риска попасть в ловушки")