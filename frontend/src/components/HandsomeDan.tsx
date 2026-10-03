// Handsome Dan, Yale's bulldog, running across the hero with a football.
// Pure HTML/CSS illustration + CSS animation (no image files).
export default function HandsomeDan() {
  return (
    <div className="hd-track" aria-hidden="true">
      <div className="hd-runner">
        <div className="hd">
          <span className="hd-tail" />
          <span className="hd-leg back far" />
          <span className="hd-leg front far" />
          <span className="hd-body">
            <span className="hd-sweater">
              <b>Y</b>
            </span>
          </span>
          <span className="hd-leg back near" />
          <span className="hd-leg front near" />
          <span className="hd-head">
            <span className="hd-ear left" />
            <span className="hd-ear right" />
            <span className="hd-brow" />
            <span className="hd-eye left" />
            <span className="hd-eye right" />
            <span className="hd-cheek" />
            <span className="hd-muzzle">
              <span className="hd-nose" />
              <span className="hd-mouth" />
              <span className="hd-tongue" />
            </span>
          </span>
          <span className="hd-ball">
            <i />
          </span>
          <span className="hd-dust" />
        </div>
      </div>
    </div>
  )
}
