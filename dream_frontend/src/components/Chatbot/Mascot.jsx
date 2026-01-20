import idle from "../../Assets/Mascot/spector_idle.png";
import thinking from "../../Assets/Mascot/spector_thinking.png";
import reply from "../../Assets/Mascot/spector_reply.png";

export default function Mascot({ state = "idle", small = false }) {
  let src = idle;

  if (state === "thinking") src = thinking;
  if (state === "replying") src = reply;

  return (
    <img
      src={src}
      alt="Spector the dream guide"
      className={`chatbot-mascot ${state} ${small ? "small" : ""}`}
    />
  );
}
