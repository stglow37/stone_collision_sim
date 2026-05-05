import pygame
import pymunk
import pymunk.pygame_util
import math

# --- 전역 상수 (충돌 감지를 위한 태그) ---
TYPE_STRIKER = 1
TYPE_TARGET_1 = 2
TYPE_TARGET_2 = 3

def create_stone(space, x, y, radius, mass, elasticity, friction, col_type, color):
    """지정된 속성으로 바둑돌을 생성하는 함수"""
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    
    shape = pymunk.Circle(body, radius)
    shape.elasticity = elasticity
    shape.friction = friction
    shape.collision_type = col_type # 누구와 충돌했는지 식별하기 위한 타입 지정
    shape.color = color
    
    space.add(body, shape)
    return body, shape

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("연속 충돌 (Three-cushion) 실험기")
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    font = pygame.font.SysFont("malgungothic", 24) # 한글 폰트 (윈도우 기준)

    # 물리 공간 초기화
    space = pymunk.Space()
    space.gravity = (0, 0)
    space.damping = 0.98  # 바닥 마찰 (서서히 멈춤)

    # 물리 파라미터
    radius = 20
    mass = 10
    restitution = 0.8
    friction = 0.2

    # 바둑돌 생성
    striker_b, striker_s = create_stone(space, 200, 400, radius, mass, restitution, friction, TYPE_STRIKER, pygame.Color("black"))
    target1_b, target1_s = create_stone(space, 400, 400, radius, mass, restitution, friction, TYPE_TARGET_1, pygame.Color("white"))
    target2_b, target2_s = create_stone(space, 600, 200, radius, mass, restitution, friction, TYPE_TARGET_2, pygame.Color("red"))

    # --- 충돌 감지 로직 (Collision Handlers) ---
    game_state = {"hit_target1": False, "hit_target2": False}

    def hit_1(arbiter, space, data):
        data["state"]["hit_target1"] = True
        return True

    def hit_2(arbiter, space, data):
        data["state"]["hit_target2"] = True
        return True

    # ---- 여기서부터 아래 코드로 교체해주세요! (Pymunk 7.x 최신 문법) ----
    
    # 타격구(1) <-> 목적구1(2) 충돌 시
    space.on_collision(TYPE_STRIKER, TYPE_TARGET_1, begin=hit_1, data={"state": game_state})

    # 타격구(1) <-> 목적구2(3) 충돌 시
    space.on_collision(TYPE_STRIKER, TYPE_TARGET_2, begin=hit_2, data={"state": game_state})

    # 목적구1(2) <-> 목적구2(3) 충돌 시
    space.on_collision(TYPE_TARGET_1, TYPE_TARGET_2, begin=hit_2, data={"state": game_state})

    # --- 상태 변수 ---
    angle_deg = -30.0  # 초기 발사 각도 (위로 30도)
    speed = 1000.0     # 발사 초기 속력 (임펄스)
    fired = False      # 발사 여부

    # 메인 루프
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not fired:
                    # 좌우 방향키로 각도 1도씩 조절
                    if event.key == pygame.K_UP:
                        angle_deg -= 1.0
                    elif event.key == pygame.K_DOWN:
                        angle_deg += 1.0
                    
                    # 스페이스바로 발사!
                    elif event.key == pygame.K_SPACE:
                        rad = math.radians(angle_deg)
                        vx = speed * math.cos(rad)
                        vy = speed * math.sin(rad)
                        striker_b.velocity = (vx, vy)
                        fired = True
                
                # R키로 시뮬레이션 초기화 (다시 쏘기)
                if event.key == pygame.K_r:
                    striker_b.position = (200, 400)
                    striker_b.velocity = (0, 0)
                    target1_b.position = (400, 400)
                    target1_b.velocity = (0, 0)
                    target2_b.position = (600, 200)
                    target2_b.velocity = (0, 0)
                    striker_b.angle = 0
                    striker_b.angular_velocity = 0
                    target1_b.angle = 0
                    target1_b.angular_velocity = 0
                    target2_b.angle = 0
                    target2_b.angular_velocity = 0
                    
                    fired = False
                    game_state["hit_target1"] = False
                    game_state["hit_target2"] = False

        # 물리 스텝 진행
        space.step(1 / 60.0)

        # 화면 렌더링
        screen.fill(pygame.Color("khaki"))
        space.debug_draw(draw_options)

        # 발사 전이라면 조준선(Aim Line) 그리기
        if not fired:
            rad = math.radians(angle_deg)
            end_x = striker_b.position.x + math.cos(rad) * 150
            end_y = striker_b.position.y + math.sin(rad) * 150
            pygame.draw.line(screen, (0, 0, 0), striker_b.position, (end_x, end_y), 2)

        # UI 텍스트 표시
        text_angle = font.render(f"발사 각도: {angle_deg:.1f} 도", True, (0, 0, 0))
        text_inst = font.render("[방향키: 위/아래] 조준  |  [Space] 발사  |  [R] 초기화", True, (50, 50, 50))
        screen.blit(text_angle, (20, 20))
        screen.blit(text_inst, (20, 60))

        # 성공 여부 표시
        if game_state["hit_target1"] and game_state["hit_target2"]:
            text_success = font.render("🎉 연속 충돌 성공! 🎉", True, (255, 50, 50))
            screen.blit(text_success, (280, 500))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()