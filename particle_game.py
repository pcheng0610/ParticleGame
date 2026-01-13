"""
手势控制粒子互动游戏 - 万剑归宗
使用OpenCV和MediaPipe实现手势识别，控制粒子群运动
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import List, Tuple, Optional

# MediaPipe版本兼容性处理
try:
    # 首先尝试标准导入方式（适用于大多数版本）
    mp_hands_module = mp.solutions.hands
    mp_drawing_module = mp.solutions.drawing_utils
    mp_drawing_styles_module = mp.solutions.drawing_styles
except AttributeError:
    # 如果mp.solutions不存在，尝试直接导入
    try:
        from mediapipe.python.solutions import hands as mp_hands_module
        from mediapipe.python.solutions import drawing_utils as mp_drawing_module
        from mediapipe.python.solutions import drawing_styles as mp_drawing_styles_module
    except ImportError:
        # 最后尝试完整路径导入
        import mediapipe.python.solutions.hands as mp_hands_module
        import mediapipe.python.solutions.drawing_utils as mp_drawing_module
        import mediapipe.python.solutions.drawing_styles as mp_drawing_styles_module


# 配置参数
class Config:
    """游戏配置参数"""
    # 窗口设置
    WINDOW_WIDTH = 2560
    WINDOW_HEIGHT = 1600
    WINDOW_NAME = "test"
    
    # 摄像头设置
    CAMERA_INDEX = 0
    
    # 粒子系统参数
    NUM_PARTICLES = 500
    MAX_SPEED = 15.0  # 提高最大速度
    MIN_SPEED = 1.0  # 提高最小速度
    SOFT_REPULSION_RADIUS = 25.0  # 粒子间软排斥半径
    
    # 意念操控算法参数
    ATTRACTION_STRENGTH = 0.6  # 目标吸引力强度
    REPULSION_STRENGTH = 0.8  # 目标排斥力强度
    PARTICLE_REPULSION = 15.0  # 粒子间排斥力（降低）
    NOISE_SCALE = 0.002  # 有机噪声缩放
    NOISE_STRENGTH = 1.0  # 有机噪声强度
    ORBIT_STRENGTH = 0.15  # 轨道旋转强度
    ARRIVE_RADIUS = 100.0  # 到达半径
    DIRECTION_STRENGTH = 0.6  # 方向控制强度
    
    # 手势识别参数
    FINGER_DISTANCE_THRESHOLD = 55  # 放宽到55像素，更容易触发
    MIN_DETECTION_CONFIDENCE = 0.6
    MIN_TRACKING_CONFIDENCE = 0.5
    
    # 视觉效果
    PARTICLE_RADIUS = 2
    PARTICLE_COLOR = (100, 200, 255)  # BGR格式：橙黄色
    LEADER_RADIUS = 6  # 核心粒子半径
    LEADER_COLOR = (255, 255, 255)  # 核心粒子颜色：白色
    PARTICLE_TRAIL_LENGTH = 0  # 禁用拖尾效果
    SHOW_HAND_LANDMARKS = True
    SHOW_VIDEO = False  # 不显示视频画面
    DEBUG_MODE = False  # 调试模式
    
    # 核心粒子参数
    LEADER_ATTRACTION = 0.25  # 核心粒子基础引力强度
    LEADER_MIN_DISTANCE = 25.0  # 最小距离
    GATHER_ATTRACTION_MULT = 5.0  # 并拢时引力倍数
    SCATTER_REPULSION = 0.3  # 张开时的轻微排斥力


class Particle:
    """粒子类"""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        """初始化粒子
        
        Args:
            x: 初始x坐标
            y: 初始y坐标
            width: 场景宽度
            height: 场景高度
        """
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.random.randn(2) * np.random.uniform(3.0, 8.0)  # 随机初始速度
        self.acceleration = np.zeros(2, dtype=float)
        self.max_speed = Config.MAX_SPEED
        self.width = width
        self.height = height
        
        # 粒子轨迹（用于绘制拖尾效果）
        self.trail: List[np.ndarray] = []
    
    def apply_force(self, force: np.ndarray):
        """施加力到粒子
        
        Args:
            force: 力向量
        """
        # 限制力的大小，避免异常抖动
        force_mag = np.linalg.norm(force)
        max_force = 3.5  # 提高最大力
        if force_mag > max_force:
            force = (force / force_mag) * max_force
        self.acceleration += force
    
    def update(self, is_leader: bool = False):
        """更新粒子位置和速度"""
        # 更新速度
        self.velocity += self.acceleration
        
        # 限制速度（上限和下限）
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed
        elif speed < Config.MIN_SPEED and speed > 0:
            self.velocity = (self.velocity / speed) * Config.MIN_SPEED
        elif speed == 0:
            # 添加随机扰动避免静止
            self.velocity = np.random.randn(2) * Config.MIN_SPEED
        
        # 平滑处理：轻微阻尼
        damping = 0.97  # 降低阻尼，保持速度
        self.velocity *= damping
        
        # 记录轨迹（如果启用）
        if Config.PARTICLE_TRAIL_LENGTH > 0:
            if len(self.trail) > Config.PARTICLE_TRAIL_LENGTH:
                self.trail.pop(0)
            self.trail.append(self.position.copy())
        
        # 更新位置
        self.position += self.velocity
        
        # 边界处理：穿透效果（从一边消失，从另一边出现）
        if self.position[0] < 0:
            self.position[0] = self.width
        elif self.position[0] > self.width:
            self.position[0] = 0
        
        if self.position[1] < 0:
            self.position[1] = self.height
        elif self.position[1] > self.height:
            self.position[1] = 0
        
        # 重置加速度
        self.acceleration = np.zeros(2, dtype=float)
    
    def get_position(self) -> np.ndarray:
        """获取粒子位置"""
        return self.position
    
    def get_velocity(self) -> np.ndarray:
        """获取粒子速度"""
        return self.velocity


class ParticleSystem:
    """粒子系统类 - 核心引导粒子机制
    
    使用一个核心粒子(leader)引导其他粒子，
    手势仅控制核心粒子，其他粒子通过吸引力跟随
    """
    
    def __init__(self, width: int, height: int, num_particles: int):
        """初始化粒子系统"""
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.time = 0.0  # 用于有机噪声
        
        # 初始化粒子，在屏幕中心区域随机生成
        center_x, center_y = width // 2, height // 2
        for i in range(num_particles):
            x = center_x + np.random.randn() * 80
            y = center_y + np.random.randn() * 80
            p = Particle(x, y, width, height)
            # 为每个粒子分配唯一的相位偏移
            p.phase = np.random.uniform(0, 2 * np.pi)
            p.noise_offset_x = np.random.uniform(0, 1000)
            p.noise_offset_y = np.random.uniform(0, 1000)
            p.is_leader = False  # 默认不是核心粒子
            self.particles.append(p)
        
        # 指定第一个粒子为核心引导粒子
        self.leader = self.particles[0]
        self.leader.is_leader = True
        # 核心粒子初始位置在中心
        self.leader.position = np.array([center_x, center_y], dtype=float)
        
        # 目标位置和状态
        self.target: Optional[np.ndarray] = None
        self.direction: Optional[np.ndarray] = None  # pointing方向
        self.scatter_center: Optional[np.ndarray] = None  # scatter模式的圆心
        self.mode: str = "free"  # "free", "gather", "scatter", "pointing"
        self.prev_mode: str = "free"  # 上一帧的模式
        self.current_attraction = Config.LEADER_ATTRACTION  # 动态引力
        
        # 特效系统
        self.effect_timer = 0.0  # 特效计时器
        self.effect_type = None  # 特效类型
        
        # 为每个粒子分配轨道半径和角速度
        for p in self.particles:
            p.orbit_radius = np.random.uniform(50, 200)  # 轨道半径
            p.orbit_speed = np.random.uniform(0.8, 1.5)  # 角速度倍率
            p.orbit_angle = np.random.uniform(0, 2 * np.pi)  # 初始角度
    
    def set_target(self, x: float, y: float):
        """设置目标位置"""
        self.target = np.array([x, y], dtype=float)
    
    def set_direction(self, dx: float, dy: float):
        """设置指向方向"""
        mag = np.sqrt(dx*dx + dy*dy)
        if mag > 0:
            self.direction = np.array([dx/mag, dy/mag], dtype=float)
        else:
            self.direction = None
    
    def set_scatter_center(self, x: float, y: float):
        """设置scatter模式的圆心位置"""
        self.scatter_center = np.array([x, y], dtype=float)
    
    def set_mode(self, mode: str):
        """设置粒子行为模式"""
        # 检测状态变化，触发特效
        if mode != self.mode:
            self._trigger_effect(self.mode, mode)
            self.prev_mode = self.mode
        self.mode = mode
    
    def _trigger_effect(self, old_mode: str, new_mode: str):
        """触发状态变化特效"""
        self.effect_timer = 30  # 特效持续约0.5秒（30帧）
        
        if new_mode == "gather" or new_mode == "pointing":
            # 聚集效果：粒子加速向内
            self.effect_type = "gather_pulse"
        elif new_mode == "scatter":
            # 散开效果：粒子瞬间向外扩散
            self.effect_type = "scatter_burst"
        elif new_mode == "free":
            # 释放效果：轻微扩散
            self.effect_type = "release"
    
    def _simplex_noise(self, x: float, y: float) -> float:
        """简化的有机噪声函数"""
        value = np.sin(x * 1.0) * np.cos(y * 1.0) * 0.5
        value += np.sin(x * 2.3 + 1.3) * np.cos(y * 2.1 + 0.7) * 0.3
        value += np.sin(x * 4.1 + 2.7) * np.cos(y * 3.9 + 1.5) * 0.2
        return value
    
    def update(self):
        """更新所有粒子 - 核心引导粒子机制"""
        self.time += 0.02
        
        # 更新特效计时器
        if self.effect_timer > 0:
            self.effect_timer -= 1
        
        # === 步骤1: 更新核心粒子 ===
        leader_force = np.zeros(2, dtype=float)
        
        # free模式下 leader也保持惯性或缓慢漂浮
        if self.mode == "free":
            if self.prev_mode == "gather":
                # 从 gather 切换过来，保持惯性
                self.leader.velocity *= 0.995
            else:
                # 非常缓慢的随机漂浮
                drift = np.array([
                    np.sin(self.time * 0.2 + self.leader.phase),
                    np.cos(self.time * 0.15 + self.leader.phase)
                ]) * 0.3
                leader_force += drift
        elif self.mode == "gather" and self.target is not None:
            # gather模式：朝目标方向猛烈冲刺
            to_target = self.target - self.leader.position
            distance = np.linalg.norm(to_target)
            if distance > 5:
                direction = to_target / distance
                # 猛烈冲刺，速度是正常的3-5倍
                leader_force += direction * Config.MAX_SPEED * 4.0
        elif self.mode == "pointing" and self.direction is not None:
            leader_force += self.direction * Config.MAX_SPEED * 1.5
        elif self.target is not None and self.mode != "scatter" and self.mode != "gather":
            to_target = self.target - self.leader.position
            distance = np.linalg.norm(to_target)
            
            if distance > 5:
                direction = to_target / distance
                speed_factor = min(distance / Config.ARRIVE_RADIUS, 1.0)
                leader_force += direction * Config.ATTRACTION_STRENGTH * Config.MAX_SPEED * speed_factor * 2.0
        
        # scatter模式：leader围绕中心圆周运动
        if self.mode == "scatter" and self.scatter_center is not None:
            # leader也做圆周运动（加快角速度）
            self.leader.orbit_angle += 0.08 * self.leader.orbit_speed
            target_x = self.scatter_center[0] + np.cos(self.leader.orbit_angle) * self.leader.orbit_radius * 0.5
            target_y = self.scatter_center[1] + np.sin(self.leader.orbit_angle) * self.leader.orbit_radius * 0.5
            to_orbit = np.array([target_x, target_y]) - self.leader.position
            leader_force += to_orbit * 0.2
        elif self.mode == "scatter":
            # 没有中心时随机运动
            scatter_x = np.sin(self.time * 1.5 + self.leader.phase) * 2.0
            scatter_y = np.cos(self.time * 1.3 + self.leader.phase * 0.7) * 2.0
            leader_force += np.array([scatter_x, scatter_y])
        
        # 核心粒子的轻微噪声
        noise_x = self._simplex_noise(
            self.leader.noise_offset_x + self.time * Config.NOISE_SCALE * 50,
            self.leader.noise_offset_y
        )
        noise_y = self._simplex_noise(
            self.leader.noise_offset_x,
            self.leader.noise_offset_y + self.time * Config.NOISE_SCALE * 50
        )
        leader_force += np.array([noise_x, noise_y]) * Config.NOISE_STRENGTH * 0.5
        
        self.leader.apply_force(leader_force)
        self.leader.update(is_leader=True)
        
        # === 步骤2: 更新其他粒子（动态引力） ===
        leader_pos = self.leader.position
        positions = np.array([p.position for p in self.particles])
        
        # 动态调节引力
        if self.mode == "gather":
            # gather模式：粒子朝目标方向突然加速
            self.current_attraction = Config.LEADER_ATTRACTION * Config.GATHER_ATTRACTION_MULT * 2.0
        elif self.mode == "pointing":
            self.current_attraction = Config.LEADER_ATTRACTION * Config.GATHER_ATTRACTION_MULT * 1.5
        elif self.mode == "scatter" or self.mode == "free":
            # scatter和free模式：无引力，粒子自由运动
            self.current_attraction = 0.0
        else:
            self.current_attraction = Config.LEADER_ATTRACTION * 0.3
        
        for i, particle in enumerate(self.particles):
            if particle.is_leader:
                continue
            
            force = np.zeros(2, dtype=float)
            
            # === scatter模式：圆周运动 ===
            if self.mode == "scatter" and self.scatter_center is not None:
                # 更新粒子的轨道角度（加快角速度）
                particle.orbit_angle += 0.08 * particle.orbit_speed
                
                # 计算目标位置（圆周上的点）
                target_x = self.scatter_center[0] + np.cos(particle.orbit_angle) * particle.orbit_radius
                target_y = self.scatter_center[1] + np.sin(particle.orbit_angle) * particle.orbit_radius
                target_pos = np.array([target_x, target_y])
                
                # 向目标位置移动的力
                to_orbit = target_pos - particle.position
                dist_to_orbit = np.linalg.norm(to_orbit)
                if dist_to_orbit > 1:
                    orbit_force = (to_orbit / dist_to_orbit) * min(dist_to_orbit * 0.2, 5.0)
                    force += orbit_force
                
                # 添加切向速度（旋转力）
                tangent = np.array([-np.sin(particle.orbit_angle), np.cos(particle.orbit_angle)])
                force += tangent * 4.0 * particle.orbit_speed
                
                # 有机噪声扰动
                noise_x = self._simplex_noise(
                    particle.noise_offset_x + self.time * Config.NOISE_SCALE * 100,
                    particle.noise_offset_y
                ) * 0.5
                noise_y = self._simplex_noise(
                    particle.noise_offset_x,
                    particle.noise_offset_y + self.time * Config.NOISE_SCALE * 100
                ) * 0.5
                force += np.array([noise_x, noise_y])
                
                # 特效处理
                if self.effect_timer > 0 and self.effect_type == "scatter_burst":
                    effect_strength = self.effect_timer / 30.0
                    to_out = particle.position - self.scatter_center
                    dist = np.linalg.norm(to_out)
                    if dist > 0:
                        force += (to_out / dist) * effect_strength * 3.0
                
                particle.apply_force(force)
                particle.update(is_leader=False)
                continue
            
            # === free模式：保持惯性或缓慢漂浮 ===
            if self.mode == "free":
                # 如果是从 gather 模式切换过来，保持冲刺惯性
                if self.prev_mode == "gather":
                    # 只施加很小的阻力，让粒子保持惯性继续移动
                    particle.velocity *= 0.995  # 很小的衰减
                    
                    # 极小的随机扰动
                    noise_x = self._simplex_noise(
                        particle.noise_offset_x + self.time * Config.NOISE_SCALE * 30,
                        particle.noise_offset_y
                    ) * 0.05
                    noise_y = self._simplex_noise(
                        particle.noise_offset_x,
                        particle.noise_offset_y + self.time * Config.NOISE_SCALE * 30
                    ) * 0.05
                    force += np.array([noise_x, noise_y])
                else:
                    # 正常的缓慢漂浮模式
                    slow_factor = 0.15  # 15%的速度
                    scatter_noise_x = self._simplex_noise(
                        particle.noise_offset_x + self.time * Config.NOISE_SCALE * 50,
                        particle.noise_offset_y
                    ) * slow_factor
                    scatter_noise_y = self._simplex_noise(
                        particle.noise_offset_x,
                        particle.noise_offset_y + self.time * Config.NOISE_SCALE * 50
                    ) * slow_factor
                    force += np.array([scatter_noise_x, scatter_noise_y])
                    
                    # 轻柔的漂浮摆动
                    sway_mult = 0.1
                    random_sway_x = np.sin(self.time * 0.5 + particle.phase * 2.0) * sway_mult
                    random_sway_y = np.cos(self.time * 0.4 + particle.phase * 1.7) * sway_mult
                    force += np.array([random_sway_x, random_sway_y])
                    
                    # 强制降低粒子速度（保持缓慢）
                    particle.velocity *= 0.92
                
                # 特效处理
                if self.effect_timer > 0 and self.effect_type == "release":
                    effect_strength = self.effect_timer / 30.0
                    force += np.random.randn(2) * effect_strength * 0.3
                
                # 应用力
                particle.apply_force(force)
                particle.update(is_leader=False)
                continue
            
            # === gather模式：猛烈冲刺 ===
            if self.mode == "gather" and self.target is not None:
                # 朝目标方向的猛烈冲刺（3-5倍速度）
                to_target = self.target - particle.position
                dist_to_target = np.linalg.norm(to_target)
                
                # 先计算方向矢量（在任何情况下都定义）
                if dist_to_target > 0:
                    burst_dir = to_target / dist_to_target
                else:
                    burst_dir = np.array([0.0, 0.0])
                
                # 只在距离较远时施加常规冲刺力
                if dist_to_target > 5:
                    # 强烈的冲刺力
                    burst_force = burst_dir * Config.MAX_SPEED * 4.0
                    force += burst_force
                
                # 轻微噪声扰动
                noise_x = self._simplex_noise(
                    particle.noise_offset_x + self.time * Config.NOISE_SCALE * 100,
                    particle.noise_offset_y
                ) * 0.3
                noise_y = self._simplex_noise(
                    particle.noise_offset_x,
                    particle.noise_offset_y + self.time * Config.NOISE_SCALE * 100
                ) * 0.3
                force += np.array([noise_x, noise_y])
                
                # 特效处理
                if self.effect_timer > 0 and self.effect_type == "gather_pulse":
                    effect_strength = self.effect_timer / 30.0
                    force += burst_dir * effect_strength * 20.0
                
                particle.apply_force(force)
                particle.update(is_leader=False)
                continue
            
            # === 非scatter/free模式：正常引力逻辑 ===
            to_leader = leader_pos - particle.position
            dist_to_leader = np.linalg.norm(to_leader)
            
            # 特效处理
            if self.effect_timer > 0:
                effect_strength = self.effect_timer / 30.0
                if self.effect_type == "gather_pulse":
                    # gather模式：朝目标方向的强烈爆发力
                    if self.target is not None:
                        to_target = self.target - particle.position
                        dist_to_target = np.linalg.norm(to_target)
                        if dist_to_target > 0:
                            burst_dir = to_target / dist_to_target
                            burst_force = burst_dir * effect_strength * 15.0
                            force += burst_force
            
            if self.current_attraction > 0 and dist_to_leader > Config.LEADER_MIN_DISTANCE:
                # 引力模式：距离越远，吸引力越大
                attraction_strength = self.current_attraction * min(dist_to_leader / 80.0, 4.0)
                direction_to_leader = to_leader / dist_to_leader
                leader_attraction = direction_to_leader * attraction_strength * Config.MAX_SPEED
                force += leader_attraction
            elif self.current_attraction < 0:
                # 排斥模式：轻微远离核心粒子
                if dist_to_leader > 0:
                    repel_strength = abs(self.current_attraction) * Config.MAX_SPEED
                    direction_from_leader = -to_leader / dist_to_leader
                    force += direction_from_leader * repel_strength
            elif dist_to_leader > 0 and dist_to_leader < Config.LEADER_MIN_DISTANCE:
                # 太近时轻微排斥
                repel_strength = (Config.LEADER_MIN_DISTANCE - dist_to_leader) / Config.LEADER_MIN_DISTANCE
                direction_from_leader = -to_leader / dist_to_leader
                force += direction_from_leader * repel_strength * 2.0
            
            # === 有机噪声扰动（增添生命力） ===
            noise_x = self._simplex_noise(
                particle.noise_offset_x + self.time * Config.NOISE_SCALE * 100,
                particle.noise_offset_y
            )
            noise_y = self._simplex_noise(
                particle.noise_offset_x,
                particle.noise_offset_y + self.time * Config.NOISE_SCALE * 100
            )
            force += np.array([noise_x, noise_y]) * Config.NOISE_STRENGTH
            
            # === 自然晃动效果（围绕核心粒子） ===
            sway_x = np.sin(self.time * 2.0 + particle.phase) * 0.5
            sway_y = np.cos(self.time * 1.5 + particle.phase * 1.3) * 0.5
            force += np.array([sway_x, sway_y])
            
            # === 粒子间软排斥（避免重叠） ===
            diff = positions - particle.position
            distances = np.linalg.norm(diff, axis=1)
            distances[i] = np.inf  # 排除自身
            
            close_mask = distances < Config.SOFT_REPULSION_RADIUS
            if np.any(close_mask):
                close_distances = distances[close_mask]
                close_diff = diff[close_mask]
                repulsion_strengths = Config.PARTICLE_REPULSION / (close_distances ** 2 + 1)
                repulsion_vectors = -close_diff / (close_distances[:, np.newaxis] + 0.1)
                particle_repulsion = np.sum(repulsion_vectors * repulsion_strengths[:, np.newaxis], axis=0)
                force += particle_repulsion
            
            # === 轻微的轨道效果 ===
            if dist_to_leader > 10:
                tangent = np.array([-to_leader[1], to_leader[0]]) / (dist_to_leader + 1)
                orbit = tangent * np.sin(self.time * 1.0 + particle.phase) * Config.ORBIT_STRENGTH
                force += orbit
            
            # 应用力
            particle.apply_force(force)
            particle.update(is_leader=False)
    
    def get_particles(self) -> List[Particle]:
        """获取所有粒子"""
        return self.particles
    
    def get_leader(self) -> Particle:
        """获取核心粒子"""
        return self.leader
    
    def apply_burst_force(self, direction: np.ndarray):
        """刨gather模式下施加爆发力，让粒子朝目标方向突然加速"""
        if direction is None:
            return
        # 归一化方向
        mag = np.linalg.norm(direction)
        if mag > 0:
            norm_dir = direction / mag
            # 对所有粒子施加强烈的爆发力
            for particle in self.particles:
                if not particle.is_leader:
                    burst_force = norm_dir * Config.MAX_SPEED * 5.0
                    particle.velocity += burst_force


class Monster:
    """怪物类 - 可移动的大球，被粒子击中会扣血"""

    def __init__(self, width: int, height: int, difficulty: int = 1, monster_type: str = "normal"):
        """初始化怪物

        Args:
            width: 场景宽度
            height: 场景高度
            difficulty: 难度等级，影响速度和躲避强度
            monster_type: 怪物类型 ("normal", "tank", "fast", "boss")
        """
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.monster_type = monster_type

        # 随机位置（避开边缘）
        margin = 100
        self.position = np.array([
            np.random.uniform(margin, width - margin),
            np.random.uniform(margin, height - margin)
        ], dtype=float)

        self.velocity = np.random.randn(2) * 2.0

        # 根据类型设置属性
        if monster_type == "tank":
            self.max_health = 20 + difficulty * 3
            self.radius = Config.PARTICLE_RADIUS * 12
            self.base_speed = 1.0 + difficulty * 0.3
            self.dodge_strength = 0.2 + difficulty * 0.1
            self.dodge_radius = 100 + difficulty * 10
            self.base_color = (180, 100, 100)  # 蓝色系
            self.score_value = 200
        elif monster_type == "fast":
            self.max_health = 5 + difficulty
            self.radius = Config.PARTICLE_RADIUS * 6
            self.base_speed = 4.0 + difficulty * 0.8
            self.dodge_strength = 1.0 + difficulty * 0.4
            self.dodge_radius = 200 + difficulty * 30
            self.base_color = (100, 255, 100)  # 绿色系
            self.score_value = 150
        elif monster_type == "boss":
            self.max_health = 50 + difficulty * 10
            self.radius = Config.PARTICLE_RADIUS * 20
            self.base_speed = 1.5 + difficulty * 0.4
            self.dodge_strength = 0.4 + difficulty * 0.15
            self.dodge_radius = 180 + difficulty * 25
            self.base_color = (100, 100, 255)  # 红色系
            self.score_value = 1000
        else:  # normal
            self.max_health = 10 + difficulty * 2
            self.radius = Config.PARTICLE_RADIUS * 8
            self.base_speed = 2.0 + difficulty * 0.5
            self.dodge_strength = 0.5 + difficulty * 0.2
            self.dodge_radius = 150 + difficulty * 20
            self.base_color = (
                np.random.randint(100, 255),
                np.random.randint(100, 255),
                np.random.randint(100, 255)
            )
            self.score_value = 100

        self.health = self.max_health
        self.max_speed = self.base_speed * 2
        self.current_color = self.base_color

        # 受伤闪烁效果
        self.hit_timer = 0
        self.hit_flash_duration = 8  # 闪烁持续帧数

        # 碰撞冷却（避免同一粒子连续扣血）
        self.hit_cooldowns = {}  # particle_id -> cooldown_frames

        # 死亡动画
        self.death_particles = []  # 死亡爆炸粒子
        self.is_dying = False
        self.death_timer = 0
    
    def update(self, particles: List[Particle]):
        """更新怪物状态"""
        # 如果正在死亡动画中
        if self.is_dying:
            self.death_timer += 1
            # 更新死亡粒子
            for dp in self.death_particles:
                dp['velocity'] *= 0.95  # 减速
                dp['position'] += dp['velocity']
                dp['life'] -= 1
            # 移除生命结束的粒子
            self.death_particles = [dp for dp in self.death_particles if dp['life'] > 0]
            return

        # 更新受伤闪烁
        if self.hit_timer > 0:
            self.hit_timer -= 1
            # 闪烁效果：在白色和原色之间切换
            if self.hit_timer % 2 == 0:
                self.current_color = (255, 255, 255)
            else:
                self.current_color = self.base_color
        else:
            self.current_color = self.base_color

        # 更新碰撞冷却
        for pid in list(self.hit_cooldowns.keys()):
            self.hit_cooldowns[pid] -= 1
            if self.hit_cooldowns[pid] <= 0:
                del self.hit_cooldowns[pid]

        # 计算躲避力（检测附近粒子）
        dodge_force = np.zeros(2, dtype=float)
        nearby_count = 0

        for particle in particles:
            if particle.is_leader:
                continue
            diff = particle.position - self.position
            dist = np.linalg.norm(diff)

            if dist < self.dodge_radius and dist > 0:
                # 远离粒子的力
                dodge_dir = -diff / dist
                strength = (self.dodge_radius - dist) / self.dodge_radius
                dodge_force += dodge_dir * strength * self.dodge_strength
                nearby_count += 1

        # 应用躲避力
        if nearby_count > 0:
            self.velocity += dodge_force

        # 随机漫游
        self.velocity += np.random.randn(2) * 0.3

        # 限制速度
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed

        # 轻微阻尼
        self.velocity *= 0.98

        # 更新位置
        self.position += self.velocity

        # 边界处理：穿透效果（从一边消失，从另一边出现）
        if self.position[0] < -self.radius:
            self.position[0] = self.width + self.radius
        elif self.position[0] > self.width + self.radius:
            self.position[0] = -self.radius

        if self.position[1] < -self.radius:
            self.position[1] = self.height + self.radius
        elif self.position[1] > self.height + self.radius:
            self.position[1] = -self.radius
    
    def check_collision(self, particles: List[Particle]) -> int:
        """检测与粒子的碰撞，返回碰撞数量"""
        hit_count = 0
        for i, particle in enumerate(particles):
            if particle.is_leader:
                continue
            
            # 检查冷却
            if i in self.hit_cooldowns:
                continue
            
            diff = particle.position - self.position
            dist = np.linalg.norm(diff)
            
            if dist < self.radius + Config.PARTICLE_RADIUS:
                hit_count += 1
                self.hit_cooldowns[i] = 30  # 30帧冷却
                
                # 粒子被弹开
                if dist > 0:
                    bounce_dir = diff / dist
                    particle.velocity = bounce_dir * Config.MAX_SPEED * 0.5
        
        return hit_count
    
    def take_damage(self, amount: int):
        """受到伤害"""
        self.health -= amount
        self.hit_timer = self.hit_flash_duration
        if self.health < 0:
            self.health = 0

        # 如果生命降到0，触发死亡动画
        if self.health <= 0 and not self.is_dying:
            self.trigger_death_animation()

    def trigger_death_animation(self):
        """触发死亡动画"""
        self.is_dying = True
        # 生成爆炸粒子
        num_particles = 30
        for _ in range(num_particles):
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(2, 8)
            self.death_particles.append({
                'position': self.position.copy(),
                'velocity': np.array([np.cos(angle) * speed, np.sin(angle) * speed]),
                'life': np.random.randint(20, 40),
                'color': self.base_color
            })

    def is_alive(self) -> bool:
        """检查是否存活"""
        return self.health > 0 and not self.is_dying

    def is_dead_animation_done(self) -> bool:
        """检查死亡动画是否结束"""
        return self.is_dying and len(self.death_particles) == 0
    
    def draw(self, frame: np.ndarray):
        """绘制怪物"""
        # 如果正在死亡动画中，绘制爆炸粒子
        if self.is_dying:
            for dp in self.death_particles:
                x, y = int(dp['position'][0]), int(dp['position'][1])
                alpha = dp['life'] / 40.0
                color = tuple(int(c * alpha) for c in dp['color'])
                cv2.circle(frame, (x, y), 3, color, -1)
            return

        x, y = int(self.position[0]), int(self.position[1])

        # 绘制主体
        cv2.circle(frame, (x, y), self.radius, self.current_color, -1)

        # 绘制外圈发光效果
        glow_color = tuple(min(255, c + 50) for c in self.current_color)
        cv2.circle(frame, (x, y), self.radius + 3, glow_color, 2)

        # Boss类型额外发光
        if self.monster_type == "boss":
            cv2.circle(frame, (x, y), self.radius + 6, glow_color, 1)

        # 绘制类型标识
        type_text = ""
        if self.monster_type == "tank":
            type_text = "TANK"
        elif self.monster_type == "fast":
            type_text = "FAST"
        elif self.monster_type == "boss":
            type_text = "BOSS"

        if type_text:
            text_size = cv2.getTextSize(type_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            text_x = x - text_size[0] // 2
            text_y = y + self.radius + 35
            cv2.putText(frame, type_text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # 绘制血量条
        bar_width = self.radius * 2
        bar_height = 6
        bar_x = x - self.radius
        bar_y = y - self.radius - 15

        # 背景
        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)

        # 血量
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        health_color = (0, 255, 0) if health_ratio > 0.5 else (0, 255, 255) if health_ratio > 0.25 else (0, 0, 255)
        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + health_width, bar_y + bar_height), health_color, -1)

        # 边框
        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 1)


class HandGestureDetector:
    """手势识别类，使用MediaPipe检测手部关键点"""
    
    def __init__(self):
        """初始化手势检测器"""
        # 使用兼容的导入方式
        self.mp_hands = mp_hands_module
        self.mp_drawing = mp_drawing_module
        self.mp_drawing_styles = mp_drawing_styles_module
        
        # 初始化Hands模型
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE
        )
        
        # 手指关键点索引
        self.INDEX_FINGER_TIP = self.mp_hands.HandLandmark.INDEX_FINGER_TIP
        self.MIDDLE_FINGER_TIP = self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP
        self.THUMB_TIP = self.mp_hands.HandLandmark.THUMB_TIP
        self.RING_FINGER_TIP = self.mp_hands.HandLandmark.RING_FINGER_TIP
        self.PINKY_TIP = self.mp_hands.HandLandmark.PINKY_TIP
    
    def process_frame(self, frame: np.ndarray) -> Optional[any]:
        """处理视频帧，检测手部
        
        Args:
            frame: 视频帧图像（BGR格式）
            
        Returns:
            手部检测结果，或None
        """
        # 转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 处理图像
        results = self.hands.process(rgb_frame)
        
        return results
    
    def draw_landmarks(self, frame: np.ndarray, results: any):
        """在画面上绘制手部关键点
        
        Args:
            frame: 视频帧图像
            results: 手部检测结果
        """
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
    
    def get_landmarks(self, results: any) -> Optional[any]:
        """获取手部关键点
        
        Args:
            results: 手部检测结果
            
        Returns:
            手部关键点或None
        """
        if results.multi_hand_landmarks:
            return results.multi_hand_landmarks[0]
        return None
    
    def release(self):
        """释放资源"""
        self.hands.close()


class GestureAnalyzer:
    """手势分析类，判断手势状态和计算目标位置"""

    def __init__(self, width: int, height: int):
        """初始化手势分析器

        Args:
            width: 画面宽度
            height: 画面高度
        """
        self.width = width
        self.height = height
        self.mp_hands = mp_hands_module

    def analyze(self, landmarks: any) -> Tuple[str, Optional[Tuple[int, int]], Optional[Tuple[float, float]], Optional[Tuple[int, int]]]:
        """分析手势状态

        Args:
            landmarks: 手部关键点

        Returns:
            (gesture_state, target_position, finger_direction, palm_center)
            gesture_state: "closed" 并拢, "open" 张开, "pointing" 指向, "none" 未检测到
            target_position: (x, y) 目标位置坐标
            finger_direction: (dx, dy) 手指指向方向向量
            palm_center: (x, y) 手掌中心位置
        """
        if landmarks is None:
            return "none", None, None, None

        # 获取各手指的关键点
        index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_mcp = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]
        index_pip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        middle_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        middle_mcp = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        middle_pip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
        ring_tip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        ring_mcp = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_MCP]
        ring_pip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP]
        pinky_tip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
        pinky_mcp = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_MCP]
        pinky_pip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP]
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]

        # 转换为像素坐标
        index_tip_x = int(index_tip.x * self.width)
        index_tip_y = int(index_tip.y * self.height)
        index_mcp_x = int(index_mcp.x * self.width)
        index_mcp_y = int(index_mcp.y * self.height)
        middle_tip_x = int(middle_tip.x * self.width)
        middle_tip_y = int(middle_tip.y * self.height)

        # 计算手掌中心（使用各手指MCP关节平均位置）
        palm_center_x = int((index_mcp.x + middle_mcp.x + ring_mcp.x + pinky_mcp.x + wrist.x) / 5 * self.width)
        palm_center_y = int((index_mcp.y + middle_mcp.y + ring_mcp.y + pinky_mcp.y + wrist.y) / 5 * self.height)
        palm_center = (palm_center_x, palm_center_y)

        # 计算食指和中指指尖之间的距离
        finger_distance = np.sqrt((index_tip_x - middle_tip_x)**2 + (index_tip_y - middle_tip_y)**2)

        # 计算手指指向方向（使用双指中点到MCP中点的方向）
        mid_tip_x = (index_tip_x + middle_tip_x) // 2
        mid_tip_y = (index_tip_y + middle_tip_y) // 2
        mid_mcp_x = (index_mcp_x + int(middle_mcp.x * self.width)) // 2
        mid_mcp_y = (index_mcp_y + int(middle_mcp.y * self.height)) // 2
        dir_x = mid_tip_x - mid_mcp_x
        dir_y = mid_tip_y - mid_mcp_y

        # 目标位置为双指中点
        target_x = mid_tip_x
        target_y = mid_tip_y

        # 判断手指伸展状态（指尖高于PIP表示伸直）
        index_extended = index_tip.y < index_pip.y
        middle_extended = middle_tip.y < middle_pip.y
        ring_extended = ring_tip.y < ring_pip.y
        pinky_extended = pinky_tip.y < pinky_pip.y

        # 计算伸展的手指数量
        extended_count = sum([index_extended, middle_extended, ring_extended, pinky_extended])

        # 判断手势状态：三种模式（按优先级排序）
        # 1. 双指定向模式：食指和中指并拢且都伸出 -> pointing
        # 2. 握拳聚集模式：伸展手指数量≤1 -> gather
        # 3. 手掌张开模式：伸展手指数量≥3 -> scatter

        is_fingers_close = finger_distance < Config.FINGER_DISTANCE_THRESHOLD

        # 优先判定：双指并拢且仅这两指伸出
        if is_fingers_close and index_extended and middle_extended and not ring_extended and not pinky_extended:
            # 食指和中指并拢（只有这两指伸出） - 定向移动模式
            return "pointing", (target_x, target_y), (dir_x, dir_y), palm_center
        elif extended_count >= 3:
            # 三个以上手指张开 - 圆周运动模式
            return "open", (target_x, target_y), None, palm_center
        elif extended_count <= 1:
            # 握拳（很少手指伸展） - 聚集加速模式
            return "gather", (target_x, target_y), (dir_x, dir_y), palm_center
        else:
            # 其他状态（伸展手指数=2但不符合pointing条件）
            return "none", (target_x, target_y), None, palm_center

    def draw_gesture_info(self, frame: np.ndarray, gesture_state: str,
                          target_position: Optional[Tuple[int, int]],
                          finger_direction: Optional[Tuple[float, float]], fps: float):
        """在画面上绘制手势信息（仅绘制目标位置和方向，不显示文本）

        Args:
            frame: 视频帧图像
            gesture_state: 手势状态
            target_position: 目标位置
            finger_direction: 手指指向方向
            fps: 帧率
        """
        # 绘制目标位置（十字准星）
        if target_position:
            # 绘制十字准星
            cross_size = 15
            cv2.line(frame, (target_position[0] - cross_size, target_position[1]),
                    (target_position[0] + cross_size, target_position[1]), (0, 255, 0), 2)
            cv2.line(frame, (target_position[0], target_position[1] - cross_size),
                    (target_position[0], target_position[1] + cross_size), (0, 255, 0), 2)
            cv2.circle(frame, target_position, 4, (0, 255, 0), -1)

            # 只在pointing模式下绘制方向箭头
            if gesture_state == "pointing" and finger_direction:
                dir_mag = np.sqrt(finger_direction[0]**2 + finger_direction[1]**2)
                if dir_mag > 0:
                    arrow_length = 60
                    end_x = int(target_position[0] + finger_direction[0] / dir_mag * arrow_length)
                    end_y = int(target_position[1] + finger_direction[1] / dir_mag * arrow_length)
                    cv2.arrowedLine(frame, target_position, (end_x, end_y), (0, 255, 255), 2, tipLength=0.3)


class GameManager:
    """游戏管理器 - 管理波次、得分、连击等"""

    def __init__(self):
        """初始化游戏管理器"""
        self.score = 0
        self.high_score = 0
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0  # 连击计时器
        self.combo_timeout = 120  # 2秒无击中则重置连击

        # 波次系统
        self.wave = 1
        self.monsters_in_wave = []
        self.monsters_defeated_this_wave = 0
        self.wave_complete = False
        self.wave_intermission_timer = 0  # 波次间休息时间
        self.wave_intermission_duration = 180  # 3秒休息

        # 击中特效粒子
        self.hit_particles = []

        # 屏幕震动
        self.screen_shake_timer = 0
        self.screen_shake_intensity = 0

    def update(self):
        """更新游戏状态"""
        # 更新连击计时器
        if self.combo > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        # 更新击中特效粒子
        for hp in self.hit_particles:
            hp['velocity'] *= 0.9
            hp['position'] += hp['velocity']
            hp['life'] -= 1
        self.hit_particles = [hp for hp in self.hit_particles if hp['life'] > 0]

        # 更新屏幕震动
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1

        # 更新波次间休息计时
        if self.wave_intermission_timer > 0:
            self.wave_intermission_timer -= 1

    def on_hit(self, damage: int):
        """当击中怪物时调用"""
        self.combo += damage
        self.combo_timer = self.combo_timeout
        if self.combo > self.max_combo:
            self.max_combo = self.combo

    def on_monster_killed(self, monster: Monster, position: np.ndarray):
        """当怪物被击败时调用"""
        base_score = monster.score_value
        combo_multiplier = 1.0 + (self.combo / 10.0)
        earned_score = int(base_score * combo_multiplier)
        self.score += earned_score
        if self.score > self.high_score:
            self.high_score = self.score

        self.monsters_defeated_this_wave += 1

        # 触发屏幕震动
        if monster.monster_type == "boss":
            self.trigger_screen_shake(20, 15)
        else:
            self.trigger_screen_shake(10, 5)

        # 生成击杀特效
        self.spawn_hit_effect(position, 50, monster.base_color)

        return earned_score

    def spawn_hit_effect(self, position: np.ndarray, count: int = 20, color: tuple = (255, 255, 0)):
        """生成击中特效"""
        for _ in range(count):
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(1, 5)
            self.hit_particles.append({
                'position': position.copy(),
                'velocity': np.array([np.cos(angle) * speed, np.sin(angle) * speed]),
                'life': np.random.randint(15, 30),
                'color': color
            })

    def trigger_screen_shake(self, duration: int, intensity: int):
        """触发屏幕震动"""
        self.screen_shake_timer = duration
        self.screen_shake_intensity = intensity

    def get_screen_shake_offset(self) -> Tuple[int, int]:
        """获取屏幕震动偏移"""
        if self.screen_shake_timer <= 0:
            return (0, 0)
        strength = (self.screen_shake_timer / 20.0) * self.screen_shake_intensity
        offset_x = int(np.random.uniform(-strength, strength))
        offset_y = int(np.random.uniform(-strength, strength))
        return (offset_x, offset_y)

    def start_wave(self, wave_number: int) -> List[dict]:
        """开始新波次，返回要生成的怪物列表"""
        self.wave = wave_number
        self.monsters_defeated_this_wave = 0
        self.wave_complete = False

        monsters_to_spawn = []

        # 每5波出现一个Boss
        if wave_number % 5 == 0:
            monsters_to_spawn.append({
                'type': 'boss',
                'difficulty': wave_number // 5
            })
        else:
            # 普通波次：根据波次数量生成不同类型的怪物
            num_monsters = min(2 + wave_number // 2, 8)  # 最多8个怪物

            for i in range(num_monsters):
                # 随机选择怪物类型
                rand = np.random.random()
                if wave_number >= 3 and rand < 0.3:
                    monster_type = 'fast'
                elif wave_number >= 2 and rand < 0.6:
                    monster_type = 'tank'
                else:
                    monster_type = 'normal'

                monsters_to_spawn.append({
                    'type': monster_type,
                    'difficulty': max(1, wave_number // 2)
                })

        self.monsters_in_wave = monsters_to_spawn
        return monsters_to_spawn

    def check_wave_complete(self, active_monsters: int) -> bool:
        """检查波次是否完成"""
        if active_monsters == 0 and self.monsters_defeated_this_wave >= len(self.monsters_in_wave):
            if not self.wave_complete:
                self.wave_complete = True
                self.wave_intermission_timer = self.wave_intermission_duration
            return True
        return False

    def can_spawn_next_wave(self) -> bool:
        """检查是否可以开始下一波次"""
        return self.wave_complete and self.wave_intermission_timer <= 0

    def draw_ui(self, frame: np.ndarray, width: int, height: int):
        """绘制游戏UI"""
        # 绘制得分
        cv2.putText(frame, f"Score: {self.score}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # 绘制最高分
        cv2.putText(frame, f"High: {self.high_score}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        # 绘制连击
        if self.combo > 0:
            combo_color = (0, 255, 255) if self.combo < 10 else (0, 200, 255) if self.combo < 20 else (0, 100, 255)
            combo_text = f"COMBO x{self.combo}!"
            text_size = cv2.getTextSize(combo_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            text_x = width // 2 - text_size[0] // 2
            cv2.putText(frame, combo_text, (text_x, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, combo_color, 3)

        # 绘制波次信息
        wave_text = f"Wave {self.wave}"
        cv2.putText(frame, wave_text, (width - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # 绘制波次进度
        monsters_left = len(self.monsters_in_wave) - self.monsters_defeated_this_wave
        cv2.putText(frame, f"Enemies: {monsters_left}", (width - 180, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        # 绘制波次间休息提示
        if self.wave_intermission_timer > 0:
            intermission_text = f"Next Wave in {self.wave_intermission_timer // 60 + 1}..."
            text_size = cv2.getTextSize(intermission_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
            text_x = width // 2 - text_size[0] // 2
            text_y = height // 2
            cv2.putText(frame, intermission_text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        # 绘制击中特效粒子
        for hp in self.hit_particles:
            x, y = int(hp['position'][0]), int(hp['position'][1])
            alpha = hp['life'] / 30.0
            color = tuple(int(c * alpha) for c in hp['color'])
            cv2.circle(frame, (x, y), 2, color, -1)

    def reset_game(self):
        """重置游戏"""
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.wave = 0
        self.monsters_in_wave = []
        self.monsters_defeated_this_wave = 0
        self.wave_complete = False
        self.wave_intermission_timer = 0
        self.hit_particles = []
        self.screen_shake_timer = 0


def main():
    """主函数"""
    print("初始化手势控制粒子游戏...")
    print("操作说明：")
    print("  - 食指和中指并拢：粒子朝指向方向快速移动")
    print("  - 握拳/双指合并：粒子聚集并突然加速")
    print("  - 手掌张开：粒子围绕手掌圆周运动")
    print("  - 用粒子攻击怪物（大球），击中减血！")
    print("  - 按 'B' 切换辅助线显示")
    print("  - 按 'R' 重新开始游戏")
    print("  - 按 'q'、'ESC' 或 'd' 退出")
    print()

    # 初始化摄像头
    cap = cv2.VideoCapture(Config.CAMERA_INDEX)  # Linux 使用默认后端
    if not cap.isOpened():
        print("错误：无法打开摄像头！")
        return

    # 设置摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.WINDOW_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.WINDOW_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率

    # 等待摄像头初始化
    import time
    time.sleep(0.5)

    # 获取实际分辨率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"摄像头分辨率: {width}x{height}")

    # 初始化手势识别
    hand_detector = HandGestureDetector()
    gesture_analyzer = GestureAnalyzer(width, height)

    # 初始化粒子系统
    particle_system = ParticleSystem(width, height, Config.NUM_PARTICLES)

    # 游戏管理器
    game_manager = GameManager()

    # 怪物系统
    monsters: List[Monster] = []
    monster_spawn_queue = []  # 待生成的怪物队列
    monster_spawn_delay = 0  # 生成延迟计时器

    # 开始第一波
    monster_spawn_queue = game_manager.start_wave(1)
    monster_spawn_delay = 60  # 1秒后开始生成

    print("游戏准备完成！")
    print("按 'q'、'ESC' 或 'd' 键退出...\n")

    # FPS计算
    prev_time = time.time()
    fps = 0

    # 辅助线显示状态
    show_helpers = True
    helper_msg_timer = 0  # 提示信息显示计时器
    
    # 主循环
    try:
        while True:
            # 读取摄像头帧
            ret, frame = cap.read()
            if not ret:
                print("错误：无法读取摄像头帧！")
                break

            # 水平翻转画面（镜像效果）
            frame = cv2.flip(frame, 1)

            # 创建粒子渲染层（纯黑色背景）
            particle_layer = np.zeros((height, width, 3), dtype=np.uint8)

            # 手部检测
            results = hand_detector.process_frame(frame)

            # 获取手部关键点
            landmarks = hand_detector.get_landmarks(results)

            # 分析手势
            gesture_state, target_position, finger_direction, palm_center = gesture_analyzer.analyze(landmarks)

            # 根据手势更新粒子系统
            if gesture_state == "pointing" and target_position:
                # 食指和中指并拢 - 定向移动
                particle_system.set_mode("pointing")
                particle_system.set_target(target_position[0], target_position[1])
                if finger_direction:
                    particle_system.set_direction(finger_direction[0], finger_direction[1])
            elif gesture_state == "gather" and target_position:
                # 握拳/双指合并 - 聚集加速
                particle_system.set_mode("gather")
                particle_system.set_target(target_position[0], target_position[1])
            elif gesture_state == "open":
                # 手掌张开 - 圆周运动
                particle_system.set_mode("scatter")
                if palm_center:
                    particle_system.set_scatter_center(palm_center[0], palm_center[1])
            else:
                particle_system.set_mode("free")
                if target_position:
                    particle_system.set_target(target_position[0], target_position[1])

            # 更新粒子
            particle_system.update()

            # 更新游戏管理器
            game_manager.update()

            # === 怪物系统更新 ===
            # 生成怪物
            if monster_spawn_delay > 0:
                monster_spawn_delay -= 1
            elif len(monster_spawn_queue) > 0:
                # 从队列中取出一个怪物生成
                monster_data = monster_spawn_queue.pop(0)
                new_monster = Monster(width, height,
                                     monster_data['difficulty'],
                                     monster_data['type'])
                monsters.append(new_monster)
                print(f"怪物生成: {monster_data['type']} (难度 {monster_data['difficulty']})")
                # 间隔0.5秒生成下一个
                monster_spawn_delay = 30

            # 更新所有怪物
            for monster in monsters[:]:  # 使用副本以便安全删除
                monster.update(particle_system.get_particles())

                # 检测碰撞
                if not monster.is_dying:
                    hits = monster.check_collision(particle_system.get_particles())
                    if hits > 0:
                        monster.take_damage(hits)
                        game_manager.on_hit(hits)
                        # 生成击中特效
                        game_manager.spawn_hit_effect(monster.position, 10, (255, 200, 0))

                # 检查怪物是否被击败
                if not monster.is_alive() and not monster.is_dying:
                    earned_score = game_manager.on_monster_killed(monster, monster.position)
                    print(f"{monster.monster_type} 被击败！获得 {earned_score} 分 (连击 x{game_manager.combo})")

                # 移除完成死亡动画的怪物
                if monster.is_dead_animation_done():
                    monsters.remove(monster)

            # 检查波次完成
            if game_manager.check_wave_complete(len(monsters)):
                print(f"第 {game_manager.wave} 波完成！")

            # 开始下一波
            if game_manager.can_spawn_next_wave():
                next_wave = game_manager.wave + 1
                monster_spawn_queue = game_manager.start_wave(next_wave)
                monster_spawn_delay = 60
                print(f"\n=== 第 {next_wave} 波开始！ ==={' BOSS战！' if next_wave % 5 == 0 else ''}")

            # 应用屏幕震动偏移
            shake_offset = game_manager.get_screen_shake_offset()

            # 绘制粒子（带连击变色）
            particle_color = Config.PARTICLE_COLOR
            if game_manager.combo > 20:
                particle_color = (150, 100, 255)  # 紫色
            elif game_manager.combo > 10:
                particle_color = (100, 150, 255)  # 橙红色

            for particle in particle_system.get_particles():
                if particle.is_leader:
                    continue  # leader粒子不绘制
                pos = particle.get_position()
                x, y = int(pos[0]) + shake_offset[0], int(pos[1]) + shake_offset[1]

                # 绘制粒子拖尾（如果启用）
                if Config.PARTICLE_TRAIL_LENGTH > 0 and len(particle.trail) > 1:
                    for i in range(1, len(particle.trail)):
                        pt1 = (int(particle.trail[i-1][0]) + shake_offset[0],
                              int(particle.trail[i-1][1]) + shake_offset[1])
                        pt2 = (int(particle.trail[i][0]) + shake_offset[0],
                              int(particle.trail[i][1]) + shake_offset[1])
                        alpha = i / len(particle.trail)
                        color = tuple(int(c * alpha) for c in particle_color)
                        cv2.line(particle_layer, pt1, pt2, color, 1)

                # 绘制粒子
                cv2.circle(particle_layer, (x, y), Config.PARTICLE_RADIUS,
                          particle_color, -1)
                # 发光效果
                cv2.circle(particle_layer, (x, y), Config.PARTICLE_RADIUS + 2,
                          particle_color, 1)

            # 绘制怪物
            for monster in monsters:
                monster.draw(particle_layer)

            # 绘制手部关键点（在黑色背景上用明亮颜色）
            if show_helpers and Config.SHOW_HAND_LANDMARKS and results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 手动绘制关键点，使用明亮颜色
                    for landmark in hand_landmarks.landmark:
                        x = int(landmark.x * width)
                        y = int(landmark.y * height)
                        cv2.circle(particle_layer, (x, y), 3, (0, 255, 0), -1)

                    # 绘制连接线
                    connections = hand_detector.mp_hands.HAND_CONNECTIONS
                    for connection in connections:
                        start_idx = connection[0]
                        end_idx = connection[1]
                        start_point = hand_landmarks.landmark[start_idx]
                        end_point = hand_landmarks.landmark[end_idx]
                        start_x, start_y = int(start_point.x * width), int(start_point.y * height)
                        end_x, end_y = int(end_point.x * width), int(end_point.y * height)
                        cv2.line(particle_layer, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

            # 计算FPS
            current_time = time.time()
            fps = 1 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0
            prev_time = current_time

            # 绘制手势信息（仅绘制目标位置和方向）
            if show_helpers:
                gesture_analyzer.draw_gesture_info(particle_layer, gesture_state,
                                                  target_position, finger_direction, fps)

            # 绘制游戏UI
            game_manager.draw_ui(particle_layer, width, height)

            # 显示辅助线状态提示
            if helper_msg_timer > 0:
                msg = "辅助线: 显示" if show_helpers else "辅助线: 隐藏"
                cv2.putText(particle_layer, msg, (width//2 - 80, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                helper_msg_timer -= 1

            # 显示画面
            cv2.imshow(Config.WINDOW_NAME, particle_layer)

            # 检测按键
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27 or key == ord('d'):  # 'q'、ESC 或 'd'
                print("退出游戏...")
                break
            elif key == ord('b') or key == ord('B'):  # 'B'键切换辅助线
                show_helpers = not show_helpers
                helper_msg_timer = 60  # 显示提示2秒
            elif key == ord('r') or key == ord('R'):  # 'R'键重新开始
                print("\n=== 重新开始游戏 ===")
                print(f"最终得分: {game_manager.score}")
                print(f"最高连击: {game_manager.max_combo}")
                print(f"到达波次: {game_manager.wave}\n")
                game_manager.reset_game()
                monsters.clear()
                monster_spawn_queue = game_manager.start_wave(1)
                monster_spawn_delay = 60
                particle_system = ParticleSystem(width, height, Config.NUM_PARTICLES)

    except KeyboardInterrupt:
        print("\n程序被中断")

    finally:
        # 释放资源
        print("释放资源...")
        cap.release()
        hand_detector.release()
        cv2.destroyAllWindows()
        print(f"\n=== 游戏统计 ===")
        print(f"最终得分: {game_manager.score}")
        print(f"最高分: {game_manager.high_score}")
        print(f"最高连击: {game_manager.max_combo}")
        print(f"到达波次: {game_manager.wave}")
        print("感谢游玩！")


if __name__ == "__main__":
    import sys
    import traceback
    
    try:
        main()
    except Exception as e:
        print("\n" + "="*50)
        print("程序发生错误！")
        print("="*50)
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        print("="*50)
        print("\n按任意键退出...")
        try:
            input()  # 等待用户按键
        except:
            import time
            time.sleep(5)  # 如果input失败，等待5秒
        sys.exit(1)
