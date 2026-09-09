# Slider FAQ

This page brings together the most common slider questions, from basic motion concepts to the formulas used for sizing a move.

## What happened to `CS axis`?

Protocol 3 dropped `CS axis`. Use `CS motors 1|2|3` and `CS servos 0..3`. Packed `IA` / `CG axis` is the sum (`motors+servos`). Count changes re-init GPIO / PIO / PWM immediately — no `RB` required (unlike the old `CS axis` path).

## How fine is RC servo PWM?

A 270° (±135°) servo over the default **0.5–2.5 ms** pulse (~13107 PWM counts) is about **0.021° per count ≈ 1.25 arc minutes**, not arc seconds. Classic analog 1–2 ms stays ~2.5′ (`CS SERVO_1_min_pulse 1000` / `max_pulse 2000`). PWM is 100 Hz, wrap 65535. See [pins.md](../mc/pins.md) and [config.md](../mc/config.md).

## What happens to Pico EXT_4 when `servos>=3`?

Pico `PIN_SERVO_3` shares **GP18** with `PIN_EXT_4`. When `servos>=3`, servo PWM steals that pin from extender `EO4`. Zero servos are GP21–23 and do not steal EXT.

---

## What is the difference between speed and acceleration?

Speed is how fast the slider moves at any moment.

Acceleration is how quickly the speed changes.

A slider can have a high top speed but still feel slow if acceleration is too low. A move with strong acceleration can feel snappy, but if it is too high it may look rough or produce vibration.

---

## What is a triangle move?

A triangle move has:

1. accelerate
2. decelerate

There is no constant-speed cruise segment.

This is common for shorter moves where the slider never reaches a steady speed before stopping.

---

## What is a trapezoid move?

A trapezoid move has three sections:

1. accelerate
2. cruise at constant speed
3. decelerate

This is the classic motion profile used for longer moves.

In a simplified linear model, the total move time is roughly:

$$
T = T_{accel} + T_{cruise} + T_{decel}
$$

---

## What is the sine-ramp profile used by this project?

This project uses a half-sine / raised-cosine acceleration profile instead of a perfectly linear acceleration ramp.

That means the speed increases smoothly, not in a straight-line ramp. The acceleration starts at zero, rises to a peak, then falls back to zero before the move settles into the next phase.

This makes the motion smoother and more natural-looking.

---

## Why does the sine-ramp profile take longer than a simple linear estimate?

Because the acceleration and deceleration are spread over a curved half-sine shape instead of a sharp linear ramp.

The result is smoother motion, but the total move consumes more time for the same speed and distance.

For a sine-ramp profile, the accel/decel time is:

$$
T_{accel} = T_{decel} = \frac{\pi V_{max}}{2a}
$$

So the full accel+decel time is:

$$
T_{ad} = \frac{\pi V_{max}}{a}
$$

---

## How do I calculate steps_per_unit for MC config?

This is the value used by SliderMC as the conversion between user units and motor steps.

For a stepper motor with:

- $N_{motor}$ = motor steps per revolution (for example 200 for a 1.8° stepper)
- $M$ = microsteps per full step (for example 8)
- $R$ = output revolutions per motor revolution through the gearbox or drive train (for a direct drive, $R = 1$)
- $U$ = travel per output revolution in user units

the step conversion is:

$$
\text{steps per unit} = \frac{N_{motor} \cdot M \cdot R}{U}
$$

where $U$ is:

- mm per spindle revolution for linear motion
- 360° for a rotary axis measured in degrees

### Linear axis with a spindle in mm

If the spindle advances $L$ mm per revolution, then:

$$
\text{steps per mm} = \frac{N_{motor} \cdot M \cdot R}{L}
$$

Example:

- 200 full steps/rev
- 8 microsteps
- 5 mm spindle travel per revolution
- direct drive, so $R = 1$

Then:

$$
\text{steps per mm} = \frac{200 \cdot 8 \cdot 1}{5} = 320
$$

So the MC config value is:

- `steps_per_unit_1 = 320`

This is the common setup for a 200-step motor with 8 microsteps and a 5 mm/rev spindle.

### Rotary axis with a gear-head in degrees

If the output shaft rotates by $\theta$ degrees per motor revolution, then:

$$
\text{steps per degree} = \frac{N_{motor} \cdot M \cdot R}{360}
$$

where $R$ is the output revolutions per motor revolution through the gearhead.

Example:

- 200 full steps/rev
- 8 microsteps
- 1:5 gear-head, so output rotates 5 revolutions per motor revolution
- axis is measured in degrees

Then:

$$
\text{steps per degree} = \frac{200 \cdot 8 \cdot 5}{360} = \frac{8000}{360} \approx 22.22
$$

So the MC config value is:

- `steps_per_unit_1 = 22.22`

with the controller configured for degree units.

### Important note

A gear-head changes the conversion factor. Always use the actual output motion per motor revolution, not just the motor’s raw step angle.

If the axis is linear, use mm per spindle revolution.
If the axis is rotary, use degrees per motor revolution after gearing.

---

## How do I estimate the move time for a given distance and speed?

If the slider is moving mostly at a steady speed with little ramp time, a quick estimate is:

$$
T \approx \frac{D}{V}
$$

where:

- $D$ = distance in mm
- $V$ = speed in mm/s
- $T$ = time in s

For a no-cruise symmetric move, the simple estimate is:

$$
T = \frac{2D}{V}
$$

This is often used for short moves where there is no long constant-speed segment.

---

## How do I estimate speed for a given distance and time?

If the move is a short symmetric move with no cruise, then:

$$
V = \frac{2D}{T}
$$

This is the quickest rule of thumb when the move is mostly accel + decel.

---

## How do I calculate acceleration from total time, speed, and cruise percent?

Let:

- $T$ = total time in seconds
- $V_{max}$ = peak speed in mm/s
- $p$ = fraction of time spent in cruise, e.g. $p = 0.5$ for 50%

### Linear trapezoid estimate

$$
a = \frac{2V_{max}}{(1-p)T}
$$

### Project sine-ramp estimate

$$
a = \frac{\pi V_{max}}{(1-p)T}
$$

### Example

Use:

- $V_{max} = 100$ mm/s
- $T = 10$ s
- $p = 0.5$

Then:

#### Trapezoid

$$
a = \frac{2 \cdot 100}{(1-0.5) \cdot 10} = 40\ \text{mm/s}^2
$$

#### Sine ramp

$$
a = \frac{\pi \cdot 100}{(1-0.5) \cdot 10} \approx 62.8\ \text{mm/s}^2
$$

---

## How do I calculate cruise percentage?

Cruise percentage can be defined in two different ways:

- by time: fraction of the total move time spent at constant speed
- by distance: fraction of the total move distance spent at constant speed

### 1) Cruise percent by time

$$
p_t = \frac{T_{cruise}}{T_{total}}
$$

This is the percentage used in the earlier acceleration formulas.

If the move is symmetric and the ramp is trapezoid-shaped:

$$
T_{total} = T_{cruise} + \frac{2V_{max}}{a}
$$

and therefore:

$$
p_t = \frac{T_{cruise}}{T_{cruise} + \frac{2V_{max}}{a}}
$$

For the sine-ramp project profile:

$$
T_{total} = T_{cruise} + \frac{\pi V_{max}}{a}
$$

so

$$
p_t = \frac{T_{cruise}}{T_{cruise} + \frac{\pi V_{max}}{a}}
$$

### 2) Cruise percent by distance

$$
p_d = \frac{D_{cruise}}{D_{total}}
$$

This is often more useful when you know only the travel distance and not the time split.

For a trapezoid profile:

$$
D_{total} = D_{cruise} + \frac{V_{max}^2}{a}
$$

so:

$$
p_d = \frac{D_{total} - \frac{V_{max}^2}{a}}{D_{total}}
= 1 - \frac{V_{max}^2}{a D_{total}}
$$

For the sine-ramp profile used here:

$$
D_{total} = D_{cruise} + \frac{\pi V_{max}^2}{2a}
$$

so:

$$
p_d = \frac{D_{total} - \frac{\pi V_{max}^2}{2a}}{D_{total}}
= 1 - \frac{\pi V_{max}^2}{2a D_{total}}
$$

### Example: 50% by time

If:

- $T_{total} = 10$ s
- $p_t = 0.5$

then:

$$
T_{cruise} = 0.5 \cdot 10 = 5\ \text{s}
$$

### Example: 50% by distance

If:

- $D_{total} = 500$ mm
- $V_{max} = 100$ mm/s
- $a = 40$ mm/s²

then for a trapezoid profile:

$$
D_{ad} = \frac{V_{max}^2}{a} = \frac{100^2}{40} = 250\ \text{mm}
$$

so:

$$
D_{cruise} = 500 - 250 = 250\ \text{mm}
$$

and therefore:

$$
p_d = \frac{250}{500} = 0.5
$$

### Practical note

Time-based cruise percentage and distance-based cruise percentage are not always the same number. They differ whenever the slider is accelerating, decelerating, or not spending the same time at the same speed over the whole move.

---

## What is the cruise percentage?

Cruise percentage is the part of the total time spent at constant speed.

Example:

- 50% cruise means half the move is constant speed
- 20% cruise means most of the move is acceleration or deceleration

More cruise usually means a longer move or a higher speed window, but only if there is enough distance to reach that speed.

---

## How much distance is used during acceleration?

### Linear trapezoid

$$
D_{accel} = \frac{V_{max}^2}{2a}
$$

### Sine ramp

$$
D_{accel} = \frac{\pi V_{max}^2}{4a}
$$

This tells you how much travel is spent before the slider reaches top speed.

---

## How much distance is used during deceleration?

The distance is the same as acceleration for a symmetric profile.

So the full accel + decel distance is:

### Linear trapezoid

$$
D_{ad} = \frac{V_{max}^2}{a}
$$

### Sine ramp

$$
D_{ad} = \frac{\pi V_{max}^2}{2a}
$$

---

## How do I estimate braking distance?

### Linear trapezoid

$$
D_{stop} = \frac{V^2}{2a}
$$

### Sine ramp

$$
D_{stop} = \frac{\pi V^2}{4a}
$$

This is useful when you want to know how much room the slider needs before it stops.

---

## How do I know whether a move is speed-limited or acceleration-limited?

A short slider move is usually acceleration-limited.

A long slider move may reach a steady speed and then be cruise-limited.

A rough rule is:

- if the distance is small, the move is usually acceleration-limited
- if the distance is large enough to reach the target speed and hold it, it is often cruise-limited

---

## What is the average speed of a move?

Average speed is simply:

$$
V_{avg} = \frac{D}{T}
$$

The average speed is lower than the peak speed whenever the move includes acceleration or deceleration.

---

## Why does my slider feel slower than the configured speed?

Because the slider spends time accelerating and decelerating.

The peak speed setting does not mean the entire move happens at that speed. For short moves, the slider may never reach the full commanded value before stopping.

---

## What is a good acceleration setting?

A good acceleration value balances:

- smooth motion
- enough speed for the shot
- no visible mechanical vibration
- enough room to stop cleanly

A practical workflow is to start with a moderate value and then increase it until the motion still looks smooth.

---

## What happens if I increase speed but not acceleration?

The move may become more time-limited by the ramping phases, especially on shorter distances.

If the slider cannot accelerate fast enough, it may never reach the commanded speed before it must slow down again.

---

## What is the fastest way to estimate a move?

Use these shortcuts:

### No-cruise move

$$
V = \frac{2D}{T}
\qquad
T = \frac{2D}{V}
$$

### Trapezoid acceleration estimate

$$
a = \frac{2V_{max}}{(1-p)T}
$$

### Sine-ramp acceleration estimate

$$
a = \frac{\pi V_{max}}{(1-p)T}
$$

These are the most useful quick checks for slider planning.

---

## How do I convert speed units?

To convert mm/s to mm/min:

$$
\text{mm/min} = \text{mm/s} \cdot 60
$$

Example:

$$
100\ \text{mm/s} = 6000\ \text{mm/min}
$$

---

## How do I plan a multi-part move?

Break the move into sections and add the times:

$$
T_{total} = T_1 + T_2 + T_3 + \cdots
$$

For example:

- accelerate
- cruise
- decelerate
- pause
- reverse move

This is the easiest way to model realistic slider choreography.

---

## Which profile should I use for camera motion?

For smooth cinematic motion:

- use lower acceleration
- use smoother ramps
- prefer a sine-ramp profile when possible

For faster or more mechanical moves:

- increase speed and acceleration carefully
- check for vibration, overshoot, or abrupt stopping

---

## What is jerk and why does it matter?

Jerk is the rate of change of acceleration.

It matters because it controls how smoothly the motion starts and stops.

A low jerk setting makes the motion feel gentle and cinematic, while a high jerk setting makes the motion more abrupt.

In many motion systems, jerk is the main difference between “smooth” and “mechanically rough” motion.

---

## How do I calculate speed from distance and time mathematically?

Let:

- $D$ = total distance in mm
- $T$ = total move time in s
- $V$ = peak speed in mm/s

### Triangle / no-cruise case

$$
D = \frac{V T}{2}
$$

so:

$$
V = \frac{2D}{T}
$$

### Trapezoid with known acceleration $a$

$$
D = V T - \frac{V^2}{a}
$$

This gives a quadratic in $V$:

$$
\frac{V^2}{a} - V T + D = 0
$$

and the valid root is:

$$
V = \frac{aT \pm \sqrt{a^2T^2 - 4aD}}{2}
$$

### Sine ramp with known acceleration $a$

$$
D = V T - \frac{\pi V^2}{2a}
$$

so:

$$
\frac{\pi V^2}{2a} - V T + D = 0
$$

and the valid solution is:

$$
V = \frac{2aT \pm \sqrt{4a^2T^2 - 8\pi a D}}{2\pi}
$$

---

## How do I calculate time from distance and speed mathematically?

Let:

- $D$ = distance in mm
- $V$ = peak speed in mm/s
- $a$ = acceleration in mm/s²

### Triangle / no-cruise case

$$
D = \frac{V T}{2}
$$

so:

$$
T = \frac{2D}{V}
$$

### Trapezoid with known acceleration

$$
D = VT - \frac{V^2}{a}
$$

rearranged:

$$
T = \frac{D}{V} + \frac{V}{a}
$$

### Sine ramp with known acceleration

$$
D = VT - \frac{\pi V^2}{2a}
$$

so:

$$
T = \frac{D}{V} + \frac{\pi V}{2a}
$$

---

## What is the practical rule of thumb?

For quick planning:

- Short move: think in triangle terms
- Long move: think in trapezoid terms
- This project: use sine-ramp equations
- For camera-like motion: use lower acceleration and smoother ramping
- For fast travel: increase speed, but verify acceleration is still smooth enough

---

## Quick reference summary

- no-cruise speed estimate: $V = \frac{2D}{T}$
- no-cruise time estimate: $T = \frac{2D}{V}$
- trapezoid accel estimate: $a = \frac{2V_{max}}{(1-p)T}$
- sine-ramp accel estimate: $a = \frac{\pi V_{max}}{(1-p)T}$
- average speed: $V_{avg} = D/T$
- triangle / no-cruise: $D = \frac{V T}{2}$
- trapezoid time with accel: $T = \frac{D}{V} + \frac{V}{a}$
- sine-ramp time with accel: $T = \frac{D}{V} + \frac{\pi V}{2a}$

This is the practical motion vocabulary for most slider planning questions.
