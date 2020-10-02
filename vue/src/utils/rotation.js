export default function(rotation) {
  while (rotation < 0) {
    rotation += 360;
  }
  while (rotation > 360) {
    rotation -= 360;
  }
  switch (rotation) {
    case 90:
    case 180:
    case 270:
      return rotation;
    default:
      return 0;
  }
}
