module CarSim

open util/ordering[Time] as tOrd

sig Time {}

sig Car {
  x, y: Int(1..4) -> Time,
  vx, vy: Int(-1..1) -> Time
} {
  all t: Time {
    one x.t and one y.t
    one vx.t and one vy.t
    /*(x.t + y.t) in (1 + 2 + 3 + 4)
    (vx.t + vy.t) in (-1 + 0 + 1)*/
    (vx.t = 0 or vy.t = 0)
  }
}

fact initiallyNotPiledUp {
  no disj c1, c2: Car | samePos[c1, c2, tOrd/first]
}

pred samePos[x1, y1: Int, x2, y2: Int] {
  x1 = x2 and y1 = y2
}

pred samePos[c1, c2: Car, t: Time] {
  samePos[c1.x.t, c1.y.t, c2.x.t, c2.y.t]
}

fun dx[c: Car, t, t': Time]: set Int {
  {i: (1+2+3+4) | (i >= c.x.t && i <= c.x.t') or (i >= c.x.t' && i <= c.x.t)}
}

fun dy[c: Car, t, t': Time]: set Int {
  {i: (1+2+3+4) | (i >= c.y.t && i <= c.y.t') or (i >= c.y.t' && i <= c.y.t)}
}

fun cellsCrossed[c: Car, t, t': Time]: set Int {
  {i: Int | some x: dx[c, t, t'] | some y: dy[c, t, t'] | i = y.mul[5].plus[x]}
}

abstract sig Event {
  t, t': Time
}

fact {
  all tx: Time - tOrd/last | some e: Event | e.t = tx and e.t' = tx.next
  all e: Event | e.t' = (e.t).next
}

sig UpdatePosition extends Event {
}
/*{
  all c: Car {
    c.x.t' = c.x.t.plus[c.vx.t]
    c.y.t' = c.y.t.plus[c.vy.t]
    c.vx.t' = c.vx.t
    c.vy.t' = c.vy.t
  }
}*/
/*{
  all c: Car | let x' = c.x.t.plus[c.vx.t], y' = c.y.t.plus[c.vy.t] {
    (no c2: Car - c |
      samePos[x', y', c2.x.t.plus[c2.vx.t], c2.y.t.plus[c2.vy.t]]
    ) implies {
      c.x.t' = x'
      c.y.t' = y'
    } else {
      // turn right: R(90) = [ 0, -1; 1, 0 ]
      let vx = c.vx.t, vy = c.vy.t {
        c.x.t' = c.x.t.plus[vx.mul[0].plus[vy.mul[-1]]]
        c.y.t' = c.y.t.plus[vx.mul[1].plus[vy.mul[0]]]
      }
    }
    c.vx.t' = c.vx.t
    c.vy.t' = c.vy.t
  }
}*/
{
  all c: Car | let x' = c.x.t.plus[c.vx.t], y' = c.y.t.plus[c.vy.t] {
    (no c2: Car - c |
      samePos[x', y', c2.x.t, c2.y.t] or
      samePos[x', y', c2.x.t.plus[c2.vx.t], c2.y.t.plus[c2.vy.t]]
    ) implies {
      c.x.t' = x'
      c.y.t' = y'
    } else {
      // don't move
      c.x.t' = c.x.t
      c.y.t' = c.y.t
    }
    c.vx.t' = c.vx.t
    c.vy.t' = c.vy.t
  }
}

pred noCollision {
  no t: Time |
    some disj c1, c2: Car |
      // samePos[c1, c2, t]
      t != tOrd/last && some (cellsCrossed[c1, t, t.next] & cellsCrossed[c2, t, t.next])
}

check {
  noCollision
} for 2 but -1..32 Int, exactly 2 Car, exactly 2 Time, exactly 1 Event


/*pred zeroSpeedAtStart {
  all c: Car | c.x.(tOrd/first) = 0 and c.y.(tOrd/first) = 0
}*/
