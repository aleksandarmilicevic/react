module CarSim

open util/ordering[Time] as tOrd

sig Time {}

sig Car {
  x, y: Int -> Time,
  vx, vy: Int -> Time
} {
  all t: Time { 
    one x.t and one y.t
    one vx.t and one vy.t
    x.t >= 0 and y.t >= 0
    x.t <= 5 and y.t <= 5
    (vx.t + vy.t) in (-1 + 0 + 1)
    (vx.t = 0 or vy.t = 0)
  }
}

pred samePos[x1, y1: Int, x2, y2: Int] {
  x1 = x2 and y1 = y2
}

pred samePos[c1, c2: Car, t: Time] {
  samePos[c1.x.t, c1.y.t, c2.x.t, c2.y.t]
}

fact initiallyNotPiledUp {
  no disj c1, c2: Car | samePos[c1, c2, tOrd/first]
}

/*sig Event {
  before, after: Time
}

fact {
  all t: Time - tOrd/last | some e: Event | e.before = t and e.after = t.next
  all e: Event | e.after = (e.before).next
}*/

pred assertStep_1_no_col_det[c: Car, t, t': Time] {
  c.x.t' = c.x.t.plus[c.vx.t]
  c.y.t' = c.y.t.plus[c.vy.t]
  c.vx.t' = c.vx.t
  c.vy.t' = c.vy.t
}

pred assertStep_2[c: Car, t, t': Time] {
  let x' = c.x.t.plus[c.vx.t], y' = c.y.t.plus[c.vy.t] {
    (no c2: Car - c | samePos[x', y', c2.x.t.plus[c2.vx.t], c2.y.t.plus[c2.vy.t]]) implies {
      c.x.t' = x'
      c.y.t' = y'      
    } else {
      -- turn right: R(90) = [ 0, -1; 1, 0 ]
      let vx = c.vx.t, vy = c.vy.t {
        c.x.t' = c.x.t.plus[vx.mul[0] - vy.mul[-1]]
        c.y.t' = c.y.t.plus[vx.mul[1] - vy.mul[0]]
      }
    }
  }
  c.vx.t' = c.vx.t
  c.vy.t' = c.vy.t
}


pred carMovement {
  all t: Time - tOrd/last | 	
    let t' = t.next |
      all c: Car |
        // assertStep_1_no_col_det[c, t, t']    
        assertStep_2[c, t, t']    
}

pred noCollision {
  no t: Time | 
    some disj c1, c2: Car | 
      samePos[c1, c2, t]
}

pred zeroSpeedAtStart {
  all c: Car | c.x.(tOrd/first) = 0 and c.y.(tOrd/first) = 0
}

check {
  carMovement implies noCollision
} for 2 but exactly 3 Car









