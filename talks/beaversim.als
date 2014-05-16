module BeaverSim

open util/ordering[Time] as tOrd

sig Time {}

sig Beaver {
  x, y: Int(1..4) -> Time,
  vx, vy: Int(-1..1) -> Time
} {
  all t: Time {
    one x.t and one y.t
    one vx.t and one vy.t
    (vx.t = 0 or vy.t = 0)
  }
}

fact initiallyNotPiledUp {
  no disj c1, c2: Beaver | samePos[c1, c2, tOrd/first]
}

pred samePos[x1, y1: Int, x2, y2: Int] {
  x1 = x2 and y1 = y2
}

pred samePos[b1, b2: Beaver, t: Time] {
  samePos[b1.x.t, b1.y.t, b2.x.t, b2.y.t]
}

fun dx[b: Beaver, t, t': Time]: set Int {
  {i: (1+2+3+4) | (i >= b.x.t && i <= b.x.t') or (i >= b.x.t' && i <= b.x.t)}
}

fun dy[b: Beaver, t, t': Time]: set Int {
  {i: (1+2+3+4) | (i >= b.y.t && i <= b.y.t') or (i >= b.y.t' && i <= b.y.t)}
}

fun cellsCrossed[b: Beaver, t, t': Time]: set Int {
  {i: Int | some x: dx[b, t, t'] | some y: dy[b, t, t'] | i = y.mul[5].plus[x]}
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
// no colision detection
{
  all b: Beaver {
    b.x.t' = b.x.t.plus[b.vx.t]
    b.y.t' = b.y.t.plus[b.vy.t]
    b.vx.t' = b.vx.t
    b.vy.t' = b.vy.t
  }
}
/*{
  all b: Beaver | let x' = b.x.t.plus[b.vx.t], y' = b.y.t.plus[b.vy.t] {
    (no b2: Beaver - b |
      samePos[x', y', b2.x.t.plus[b2.vx.t], b2.y.t.plus[b2.vy.t]]
    ) implies {
      b.x.t' = x'
      b.y.t' = y'
    } else {
      // turn right: R(90) = [ 0, -1; 1, 0 ]
      let vx = b.vx.t, vy = b.vy.t {
        b.x.t' = b.x.t.plus[vx.mul[0].plus[vy.mul[-1]]]
        b.y.t' = b.y.t.plus[vx.mul[1].plus[vy.mul[0]]]
      }  
    }
    b.vx.t' = b.vx.t
    b.vy.t' = b.vy.t
  }
}*/

check noCollision {
  no t: Time |
    some disj b1, b2: Beaver |
      samePos[b1, b2, t]
      // t != tOrd/last && some (cellsCrossed[b1, t, t.next] & cellsCrossed[b2, t, t.next])
} for 2 but 7 Int, 3 Beaver, exactly 2 Time, exactly 1 Event
