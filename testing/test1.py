#260505

import pygame
import pymunk
import pymunk.pygame_util

def create_stone(space, x, y, radius, mass, elasticity, friction):
    """바둑돌(원판)을 생성하여 물리 공간에 추가하는 함수"""
    # 1. 관성 모멘트 계산 (원판 형태)
    moment = pymunk.moment_for_circle(mass, 0, radius)
    
    # 2. Body(무게 중심과 운동 상태) 생성
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    
    # 3. Shape(형태와 재질) 생성
    shape = pymunk.Circle(body, radius)
    shape.elasticity = elasticity  # 반발 계수 (0~1)
    shape.friction = friction      # 마찰 계수
    
    # 4. Space에 추가
    space.add(body, shape)
    return body, shape

def main():
    # --- Pygame 화면 초기화 ---
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("바둑돌 빗맞은 충돌 시뮬레이션 (Pymunk)")
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # --- Pymunk 물리 공간 초기화 ---
    space = pymunk.Space()
    space.gravity = (0, 0)  # 위에서 내려다보는 시점이므로 중력 0
    space.damping = 0.99    # 바닥과의 구름/미끄러짐 마찰(공기저항처럼 속도를 서서히 줄임)

    # 물리 파라미터 설정
    stone_radius = 20
    stone_mass = 10
    restitution = 0.8  # 반발 계수 e
    friction = 0.2     # 마찰 계수 mu

    # --- 바둑돌 배치 ---
    # 1. 움직이는 바둑돌 (Striker) - 화면 왼쪽에서 출발
    striker_body, striker_shape = create_stone(space, 100, 300, stone_radius, stone_mass, restitution, friction)
    striker_shape.color = pygame.Color("black")
    # 오른쪽(x축 방향)으로 강하게 밀어줌 (초기 속도)
    striker_body.velocity = (500, 0)

    # 2. 멈춰있는 바둑돌 (Target) - 화면 중앙에 배치
    # ★ 빗맞은 충돌(Oblique)을 유도하기 위해 y좌표를 살짝 어긋나게(310) 배치합니다.
    target_body, target_shape = create_stone(space, 400, 380, stone_radius, stone_mass, restitution, friction)
    target_shape.color = pygame.Color("white")

    # --- 메인 시뮬레이션 루프 ---
    running = True
    while running:
        # 이벤트 처리 (창 닫기 등)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 물리 연산 진행 (1초에 60프레임 기준)
        space.step(1 / 60.0)

        # 화면 그리기
        screen.fill(pygame.Color("khaki"))  # 바둑판 색상
        space.debug_draw(draw_options)      # 물리 객체들을 화면에 그림
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()