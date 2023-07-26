export const nextElementInList = <T>(arr: T[], val: T): T => {
  const idx = arr.indexOf(val);
  const nextIdx = (idx + 1) % arr.length;
  return arr[nextIdx];
};
