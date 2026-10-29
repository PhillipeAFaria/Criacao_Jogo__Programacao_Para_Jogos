"""Passos fixos com recuperação limitada para não bloquear a interface."""
class FixedStepper:
    def __init__(self, step=1 / 60, max_steps=15):
        self.step = step
        self.max_steps = max_steps
        self.remainder = 0.0
        self.dropped_seconds = 0.0

    def advance(self, seconds, update):
        accepted = min(max(0.0, seconds), self.step * self.max_steps)
        self.dropped_seconds += max(0., seconds - accepted)
        self.remainder += accepted
        count = 0
        while self.remainder + 1e-10 >= self.step and count < self.max_steps:
            update(self.step)
            self.remainder = max(0., self.remainder - self.step)
            count += 1
        return count

