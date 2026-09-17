3A — Shot lifetime / range
     Bullets should not fly forever.

3B — Shot world wrapping
     Shots crossing an edge continue from the opposite edge
     while their lifetime remains.

3C — Shot-count limiting
     Prevent unlimited simultaneous bullets.
     This gives the weapon the constrained arcade feel.

3D — Collision cleanup
     Make sure one shot can destroy only one asteroid,
     splitting/removal order is safe,
     and we don't accidentally process dead sprites twice.

3E — Player collision refinement
     Replace our temporary expanded circular Player hitbox
     with the actual ship geometry / triangle-vs-circle system.

3F — Collision/event telemetry
     Verify:
         "shot_fired"
         "asteroid_hit"
         "player_hit"
         "asteroid_split"
     and anything else needed for later accuracy/stats.