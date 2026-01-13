// 游戏配置
const CONFIG = {
    NUM_PARTICLES: 300,
    MAX_SPEED: 15,
    MIN_SPEED: 1,
    PARTICLE_RADIUS: 2,
    PARTICLE_COLOR: '#64C8FF',
    LEADER_RADIUS: 6,
    LEADER_COLOR: '#FFFFFF'
};

// 全局变量
let canvas, ctx, video;
let particles = [];
let monsters = [];
let gameState = {
    score: 0,
    wave: 1,
    combo: 0,
    fps: 0
};
let hands, camera;
let handResults = null;
let lastTime = Date.now();
let frameCount = 0;

// 粒子类
class Particle {
    constructor(x, y, width, height) {
        this.position = { x, y };
        this.velocity = {
            x: (Math.random() - 0.5) * 6,
            y: (Math.random() - 0.5) * 6
        };
        this.acceleration = { x: 0, y: 0 };
        this.maxSpeed = CONFIG.MAX_SPEED;
        this.width = width;
        this.height = height;
        this.isLeader = false;
    }

    applyForce(force) {
        const forceMag = Math.sqrt(force.x ** 2 + force.y ** 2);
        const maxForce = 3.5;
        if (forceMag > maxForce) {
            force.x = (force.x / forceMag) * maxForce;
            force.y = (force.y / forceMag) * maxForce;
        }
        this.acceleration.x += force.x;
        this.acceleration.y += force.y;
    }

    update() {
        // 更新速度
        this.velocity.x += this.acceleration.x;
        this.velocity.y += this.acceleration.y;

        // 限制速度
        const speed = Math.sqrt(this.velocity.x ** 2 + this.velocity.y ** 2);
        if (speed > this.maxSpeed) {
            this.velocity.x = (this.velocity.x / speed) * this.maxSpeed;
            this.velocity.y = (this.velocity.y / speed) * this.maxSpeed;
        }

        // 阻尼
        this.velocity.x *= 0.97;
        this.velocity.y *= 0.97;

        // 更新位置
        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;

        // 边界处理（穿透效果）
        if (this.position.x < 0) this.position.x = this.width;
        else if (this.position.x > this.width) this.position.x = 0;
        if (this.position.y < 0) this.position.y = this.height;
        else if (this.position.y > this.height) this.position.y = 0;

        // 重置加速度
        this.acceleration.x = 0;
        this.acceleration.y = 0;
    }

    draw(ctx) {
        if (this.isLeader) {
            ctx.fillStyle = CONFIG.LEADER_COLOR;
            ctx.beginPath();
            ctx.arc(this.position.x, this.position.y, CONFIG.LEADER_RADIUS, 0, Math.PI * 2);
            ctx.fill();
        } else {
            ctx.fillStyle = CONFIG.PARTICLE_COLOR;
            ctx.beginPath();
            ctx.arc(this.position.x, this.position.y, CONFIG.PARTICLE_RADIUS, 0, Math.PI * 2);
            ctx.fill();

            // 发光效果
            ctx.strokeStyle = CONFIG.PARTICLE_COLOR;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(this.position.x, this.position.y, CONFIG.PARTICLE_RADIUS + 2, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
}

// 怪物类
class Monster {
    constructor(width, height) {
        this.position = {
            x: Math.random() * (width - 200) + 100,
            y: Math.random() * (height - 200) + 100
        };
        this.velocity = {
            x: (Math.random() - 0.5) * 4,
            y: (Math.random() - 0.5) * 4
        };
        this.radius = 40;
        this.health = 10;
        this.maxHealth = 10;
        this.color = `hsl(${Math.random() * 360}, 70%, 50%)`;
        this.width = width;
        this.height = height;
    }

    update() {
        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;

        // 边界反弹
        if (this.position.x < this.radius || this.position.x > this.width - this.radius) {
            this.velocity.x *= -1;
        }
        if (this.position.y < this.radius || this.position.y > this.height - this.radius) {
            this.velocity.y *= -1;
        }
    }

    checkCollision(particle) {
        const dx = particle.position.x - this.position.x;
        const dy = particle.position.y - this.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        return distance < this.radius + CONFIG.PARTICLE_RADIUS;
    }

    takeDamage(amount) {
        this.health -= amount;
        return this.health <= 0;
    }

    draw(ctx) {
        // 绘制怪物
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.position.x, this.position.y, this.radius, 0, Math.PI * 2);
        ctx.fill();

        // 绘制血条
        const barWidth = this.radius * 2;
        const barHeight = 6;
        const barX = this.position.x - this.radius;
        const barY = this.position.y - this.radius - 15;

        ctx.fillStyle = 'rgba(50, 50, 50, 0.8)';
        ctx.fillRect(barX, barY, barWidth, barHeight);

        const healthRatio = this.health / this.maxHealth;
        ctx.fillStyle = healthRatio > 0.5 ? '#00ff00' : healthRatio > 0.25 ? '#ffff00' : '#ff0000';
        ctx.fillRect(barX, barY, barWidth * healthRatio, barHeight);
    }
}

// 初始化游戏
function initGame() {
    canvas = document.getElementById('game-canvas');
    ctx = canvas.getContext('2d');
    video = document.getElementById('video');

    // 设置画布大小
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // 初始化粒子
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    for (let i = 0; i < CONFIG.NUM_PARTICLES; i++) {
        const angle = (i / CONFIG.NUM_PARTICLES) * Math.PI * 2;
        const radius = Math.random() * 100;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        particles.push(new Particle(x, y, canvas.width, canvas.height));
    }

    // 设置核心粒子
    particles[0].isLeader = true;

    // 生成初始怪物
    spawnMonsters(3);
}

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

function spawnMonsters(count) {
    for (let i = 0; i < count; i++) {
        monsters.push(new Monster(canvas.width, canvas.height));
    }
}

// MediaPipe 手势识别
async function setupMediaPipe() {
    const loadingText = document.getElementById('loading-text');

    try {
        loadingText.textContent = '正在初始化 MediaPipe Hands...';

        // 初始化 MediaPipe Hands
        hands = new Hands({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
            }
        });

        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.6,
            minTrackingConfidence: 0.5
        });

        hands.onResults(onHandResults);

        loadingText.textContent = '正在请求摄像头权限...';

        // 使用标准的 getUserMedia API（更好的兼容性）
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: 640,
                height: 480,
                facingMode: 'user'
            }
        });

        video.srcObject = stream;
        await video.play();

        loadingText.textContent = '加载完成！点击开始游戏';

        // 开始处理视频帧
        processVideoFrame();

    } catch (error) {
        console.error('MediaPipe 初始化失败:', error);
        showError(`无法访问摄像头或初始化手势识别。\n\n错误详情: ${error.message}\n\n请确保：\n1. 授予浏览器摄像头权限\n2. 使用 HTTPS 或 localhost\n3. 摄像头未被其他应用占用`);
    }
}

// 处理视频帧
async function processVideoFrame() {
    if (!video || !hands) return;

    try {
        await hands.send({ image: video });
    } catch (error) {
        console.error('处理帧失败:', error);
    }

    requestAnimationFrame(processVideoFrame);
}

function onHandResults(results) {
    handResults = results;
}

// 手势分析
function analyzeGesture() {
    if (!handResults || !handResults.multiHandLandmarks || handResults.multiHandLandmarks.length === 0) {
        return { mode: 'free', target: null };
    }

    const landmarks = handResults.multiHandLandmarks[0];

    // 获取关键点（转换为画布坐标）
    const indexTip = {
        x: landmarks[8].x * canvas.width,
        y: landmarks[8].y * canvas.height
    };
    const middleTip = {
        x: landmarks[12].x * canvas.width,
        y: landmarks[12].y * canvas.height
    };
    const palmCenter = {
        x: landmarks[9].x * canvas.width,
        y: landmarks[9].y * canvas.height
    };

    // 计算手指间距
    const fingerDistance = Math.sqrt(
        (indexTip.x - middleTip.x) ** 2 +
        (indexTip.y - middleTip.y) ** 2
    );

    // 判断手势
    const target = {
        x: (indexTip.x + middleTip.x) / 2,
        y: (indexTip.y + middleTip.y) / 2
    };

    if (fingerDistance < 50) {
        return { mode: 'gather', target };
    } else {
        // 检查有多少手指伸出
        const fingersExtended = [8, 12, 16, 20].filter(i =>
            landmarks[i].y < landmarks[i - 2].y
        ).length;

        if (fingersExtended >= 3) {
            return { mode: 'scatter', target: palmCenter };
        } else {
            return { mode: 'free', target };
        }
    }
}

// 更新粒子
function updateParticles() {
    const gesture = analyzeGesture();
    const leader = particles[0];

    // 更新核心粒子
    if (gesture.mode === 'gather' && gesture.target) {
        const dx = gesture.target.x - leader.position.x;
        const dy = gesture.target.y - leader.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 5) {
            leader.applyForce({
                x: (dx / distance) * CONFIG.MAX_SPEED * 2,
                y: (dy / distance) * CONFIG.MAX_SPEED * 2
            });
        }
    }

    leader.update();

    // 更新其他粒子
    for (let i = 1; i < particles.length; i++) {
        const particle = particles[i];

        if (gesture.mode === 'gather') {
            // 聚集模式：跟随核心粒子
            const dx = leader.position.x - particle.position.x;
            const dy = leader.position.y - particle.position.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > 25) {
                particle.applyForce({
                    x: (dx / distance) * 0.5,
                    y: (dy / distance) * 0.5
                });
            }
        } else if (gesture.mode === 'scatter' && gesture.target) {
            // 散开模式：围绕手掌旋转
            const dx = particle.position.x - gesture.target.x;
            const dy = particle.position.y - gesture.target.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > 0) {
                particle.applyForce({
                    x: -dy / distance * 2,
                    y: dx / distance * 2
                });
            }
        }

        // 添加噪声
        particle.applyForce({
            x: (Math.random() - 0.5) * 0.5,
            y: (Math.random() - 0.5) * 0.5
        });

        particle.update();
    }
}

// 更新怪物和碰撞检测
function updateMonsters() {
    for (let i = monsters.length - 1; i >= 0; i--) {
        const monster = monsters[i];
        monster.update();

        // 检测与粒子的碰撞
        let hitCount = 0;
        for (const particle of particles) {
            if (monster.checkCollision(particle)) {
                hitCount++;
            }
        }

        if (hitCount > 0) {
            if (monster.takeDamage(hitCount)) {
                // 怪物被击败
                monsters.splice(i, 1);
                gameState.score += 100;
                gameState.combo += 1;

                // 如果所有怪物被清除，进入下一波
                if (monsters.length === 0) {
                    gameState.wave++;
                    spawnMonsters(3 + gameState.wave);
                }
            }
        }
    }
}

// 游戏主循环
function gameLoop() {
    // 清空画布
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 更新游戏对象
    updateParticles();
    updateMonsters();

    // 绘制粒子
    for (const particle of particles) {
        particle.draw(ctx);
    }

    // 绘制怪物
    for (const monster of monsters) {
        monster.draw(ctx);
    }

    // 绘制手部关键点（调试用）
    if (handResults && handResults.multiHandLandmarks) {
        drawHands(ctx, handResults);
    }

    // 更新 FPS
    frameCount++;
    const now = Date.now();
    if (now - lastTime >= 1000) {
        gameState.fps = frameCount;
        frameCount = 0;
        lastTime = now;
    }

    // 更新 UI
    updateUI();

    requestAnimationFrame(gameLoop);
}

function drawHands(ctx, results) {
    if (results.multiHandLandmarks) {
        for (const landmarks of results.multiHandLandmarks) {
            // 绘制关键点
            ctx.fillStyle = '#00ff00';
            for (const landmark of landmarks) {
                const x = landmark.x * canvas.width;
                const y = landmark.y * canvas.height;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, Math.PI * 2);
                ctx.fill();
            }

            // 绘制连接线
            ctx.strokeStyle = '#00ff00';
            ctx.lineWidth = 2;
            const connections = [
                [0, 1], [1, 2], [2, 3], [3, 4],  // 拇指
                [0, 5], [5, 6], [6, 7], [7, 8],  // 食指
                [0, 9], [9, 10], [10, 11], [11, 12],  // 中指
                [0, 13], [13, 14], [14, 15], [15, 16],  // 无名指
                [0, 17], [17, 18], [18, 19], [19, 20],  // 小指
                [5, 9], [9, 13], [13, 17]  // 手掌
            ];

            for (const [start, end] of connections) {
                ctx.beginPath();
                ctx.moveTo(landmarks[start].x * canvas.width, landmarks[start].y * canvas.height);
                ctx.lineTo(landmarks[end].x * canvas.width, landmarks[end].y * canvas.height);
                ctx.stroke();
            }
        }
    }
}

function updateUI() {
    document.getElementById('fps').textContent = gameState.fps;
    document.getElementById('score').textContent = gameState.score;
    document.getElementById('wave').textContent = gameState.wave;
    document.getElementById('combo').textContent = gameState.combo;
}

// UI 控制函数
function toggleVideo() {
    const video = document.getElementById('video');
    video.style.display = video.style.display === 'none' ? 'block' : 'none';
}

function toggleInstructions() {
    const instructions = document.getElementById('instructions');
    instructions.style.display = instructions.style.display === 'none' ? 'block' : 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    errorText.textContent = message;
    errorDiv.style.display = 'block';
}

// 开始游戏
async function startGame() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('game-container').style.display = 'block';

    initGame();
    gameLoop();
}

// 页面加载时初始化 MediaPipe
window.addEventListener('load', () => {
    setupMediaPipe();
});
