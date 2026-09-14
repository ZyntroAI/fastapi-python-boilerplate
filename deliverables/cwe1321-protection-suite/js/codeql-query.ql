/**
 * @name js/prototype-pollution
 * @description Detects direct writes to `__proto__`, `prototype`, and
 *   `constructor` object members that can cause prototype pollution (CWE-1321).
 * @kind problem
 * @id js/cwe1321/prototype-pollution
 * @problem.severity error
 * @precision high
 * @tags security
 *       external/cwe/cwe-1321
 */

import javascript

/** A data-flow sink is any write (assignment or update) of a property. */
predicate isSink(DataFlow::Node sink) {
  sink.asExpr().(AssignExpr).getLhs() instanceof DataFlow::PropAccess or
  sink.asExpr().(AssignExpr).getLhs() instanceof DataFlow::IndexExpr
}

/** Get the property name written by an assignment, if it is statically known. */
string writtenPropName(DataFlow::Node sink) {
  exists(DataFlow::PropAccess pa |
    pa = sink.asExpr().(AssignExpr).getLhs() and result = pa.getPropertyName()
  )
  or
  exists(DataFlow::IndexExpr idx |
    idx = sink.asExpr().(AssignExpr).getLhs() and
    idx.getIndex() instanceof DataFlow::StringLiteral and
    result = idx.getIndex().(DataFlow::StringLiteral).getValue()
  )
}

from DataFlow::Node sink
where
  isSink(sink) and
  (writtenPropName(sink) = "__proto__" or
   writtenPropName(sink) = "prototype" or
   writtenPropName(sink) = "constructor")
select sink,
  "Prototype-polluting write to '$@' (CWE-1321). Block or filter this key.",
  writtenPropName(sink)
