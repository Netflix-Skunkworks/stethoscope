export default function sortBy (collection, valueFunction) {
  return collection.slice(0).sort((a, b) => {
    const valA = valueFunction(a)
    const valB = valueFunction(b)
    if (valA < valB) return -1
    if (valA > valB) return 1
    return 0
  })
}
