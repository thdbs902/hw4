// DD, the CC bulldog mascot, drawn in HTML/CSS only (no image file).
export default function DDAvatar({ size = 44 }: { size?: number }) {
  return (
    <span className="dd" style={{ width: size, height: size }} aria-hidden="true">
      <span className="dd-ear l" />
      <span className="dd-ear r" />
      <span className="dd-face">
        <span className="dd-eye l" />
        <span className="dd-eye r" />
        <span className="dd-muzzle">
          <span className="dd-nose" />
        </span>
      </span>
      <span className="dd-collar">Y</span>
    </span>
  )
}
