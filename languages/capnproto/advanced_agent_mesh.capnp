@0xbfe7d4ab63a0c101;

struct Mission {
  id @0 :Text;
  capability @1 :Text;
  inputSha256 @2 :Data;
}

struct Receipt {
  missionId @0 :Text;
  accepted @1 :Bool;
  reason @2 :Text;
  outputSha256 @3 :Data;
}

interface Specialist {
  execute @0 (mission :Mission) -> (receipt :Receipt);
}

interface Router {
  resolve @0 (capability :Text) -> (specialist :Specialist);
  health @1 () -> (ready :Bool, detail :Text);
}
