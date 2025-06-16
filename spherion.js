// Minimal Level-0 + refinement logic in JS
export function cartesianToSpherion(x,y,z){
  const sign = (v)=> (v>=0? +1 : -1);
  const r = Math.hypot(x,y,z);
  return {sign_x:sign(x), sign_y:sign(y), sign_z:sign(z), radius:r, path:[]};
}
export function refineByMeasurement(coord,x,y,z,levels=1,max=5){
  const out = JSON.parse(JSON.stringify(coord));          // deep copy
  const abs = Math.abs, path = out.path;
  for(let i=0; i<levels && path.length<max; ++i){
    const lvl = path.length+1;
    const threshold = 0.5**(lvl+1);
    const bit = (val)=> abs(val/out.radius) >= threshold ? +1 : -1;
    path.push([bit(x),bit(y),bit(z)]);
  }
  return out;
}
// helper (centre-of-cell estimate, mirrors Python)
export function toCartesian(coord){
  const invRoot3 = 1/Math.sqrt(3);
  let x = coord.sign_x*coord.radius*invRoot3;
  let y = coord.sign_y*coord.radius*invRoot3;
  let z = coord.sign_z*coord.radius*invRoot3;
  let step = coord.radius*invRoot3/4;
  coord.path.forEach(([bx,by,bz],lvl)=>{
    x += bx*step; y += by*step; z += bz*step; step/=2;
  });
  return [x,y,z];
}
// attach for convenience
Object.assign(cartesianToSpherion.prototype,{toCartesian});
export function extend(obj){obj.toCartesian=()=>toCartesian(obj);return obj;}