# API design

Apply API prescriptions to reusable libraries; for applications, prefer the
simplest interface that serves known callers. Check existing public contracts
before changing signatures. [Source](https://google.github.io/styleguide/rustguide.html#api-design-context).

## API-01 — Borrow flexible immutable inputs

When only the contents are needed, accept `&T`, `&[T]`, `&str`, or
`Option<&T>` instead of `&Box<T>`, `&Vec<T>`, `&String`, or `&Option<T>`.
Retain a container-specific input if its capabilities are actually required.
The goal is accepting more callers without copies, not hiding needed semantics.
[Source](https://google.github.io/styleguide/rustguide.html#flexible-references).

## API-02 — Choose collection flexibility from actual use

For reusable libraries, prefer an iterator return when it avoids imposing an
allocation or collection on callers. Return an owned collection when most callers
need it, it will be randomly indexed, the implementation is clearer as a loop
and allocation is acceptable, constructing the collection is the purpose, or
the collection already exists. In applications, a vector is often the simpler API.

If a reusable library only iterates over input, consider an iterator or
`impl IntoIterator`. An application may use a slice when extra flexibility or
performance is unnecessary. Consider `impl Into<T>` inputs in library APIs
when call-site ergonomics justify generics and code size; application code should
almost never need them. Do not mechanically generalize every signature.
Sources: [returns](https://google.github.io/styleguide/rustguide.html#return-iterators),
[inputs](https://google.github.io/styleguide/rustguide.html#accept-iterators),
[Into](https://google.github.io/styleguide/rustguide.html#accepting-into).

## API-03 — Make distinctions visible in types

Use an enum for a boolean argument whose meaning is unclear at the call site;
a meaningful inline argument comment is another option. Do not replace every
boolean regardless of clarity. Use newtypes for distinct semantics, a dedicated
API, future representation changes, or easily confused values. Prefer named
fields over positional tuples except for newtypes and unambiguous local use.
Sources: [booleans](https://google.github.io/styleguide/rustguide.html#enum-vs-bool),
[newtypes](https://google.github.io/styleguide/rustguide.html#newtypes-vs-type-aliases),
[fields](https://google.github.io/styleguide/rustguide.html#prefer-named-fields).

## API-04 — Introduce traits for a purpose

Use traits for generic bounds, static/dynamic dispatch in interfaces, or justified
extension methods, not simply to organize methods. Prefer standard traits when
their contract matches a custom method; an inherent method may coexist for
discoverability. Derive implementations when a derive expresses the intended
semantics. Low-level libraries should anticipate useful trait impls; applications
add them when needed. Library parameters generally prefer generics over
`dyn Trait`, with code-size needs an exception.
Sources: [purpose](https://google.github.io/styleguide/rustguide.html#trait-vs-inherent-impl),
[standard traits](https://google.github.io/styleguide/rustguide.html#known-traits),
[derive](https://google.github.io/styleguide/rustguide.html#derive),
[timing](https://google.github.io/styleguide/rustguide.html#traits-yagni),
[dispatch](https://google.github.io/styleguide/rustguide.html#generics-vs-dyn-trait).

Extension traits normally belong to the owner of the extended type and use an
`Ext` suffix. Foundational libraries may add widely useful, well-known extensions.
Traits used as input abstractions over foreign types are a different case.
[Source](https://google.github.io/styleguide/rustguide.html#extension-traits).

## API-05 — Choose trait promises deliberately

For public-field types, consider traits shared by all fields. Error types should
be `Copy` where possible; promise `Copy` only if it is likely to remain valid.
Most types should be `Clone`, except external-resource owners. Provide `Default`
for a default state or a parameterless `new()`. Equality/ordering operators can
use `PartialEq`/`PartialOrd`; add `Eq`/`Ord` only when the stronger laws hold.
Likely map/cache keys need `Hash` and `Eq`, and `Ord` for a clear total order.
[Source](https://google.github.io/styleguide/rustguide.html#important-traits).

Pair an important construction `From` implementation with a discoverable inherent
constructor. All-public options structs should implement `Default` for struct
update syntax. Do not replace a meaningful custom default with a derive that
changes behavior.
Sources: [construction](https://google.github.io/styleguide/rustguide.html#from-impls),
[options](https://google.github.io/styleguide/rustguide.html#options-should-implement-default).

## API-06 — Protect evolvable external APIs without breaking construction

Use `#[non_exhaustive]` on evolving enums and public-field structs used across
teams. Exceptions include fixed ontologies/stable shapes, coordinated migrations
where the author fixes callers, and limited usage where widespread breakage is
not a concern. Structs intended for external struct-update construction are
also an exception: adding the attribute prevents that construction.

Check real consumers and release compatibility before suggesting this attribute.
An internal `pub` type is not automatically a cross-team API.
Sources: [enums](https://google.github.io/styleguide/rustguide.html#non-exhaustive-enums),
[structs](https://google.github.io/styleguide/rustguide.html#non-exhaustive-structs).

## API-07 — Keep accessors and API commitments predictable

Use `foo`, `foo_mut`, `set_foo`, `take_foo` (clear and return the old value),
and `replace_foo` (replace and return the old value) as appropriate.
Closure accessors `with_foo`/`with_mut_foo` can hide interior-mutability guards
or allow follow-up validation when replacing/cloning the value is unsuitable.
They can forward the closure's return value. A single mutable closure accessor
may also use `with_foo`. Supply `is_empty` with `len`.
Sources: [accessors](https://google.github.io/styleguide/rustguide.html#getters-and-setters),
[closures](https://google.github.io/styleguide/rustguide.html#closure-accessors),
[pairs](https://google.github.io/styleguide/rustguide.html#expected-api-sets).

Treat foreign `#[doc(hidden)]` items as private. Mark public functions `const`
only if you expect to preserve that promise or will help migrate clients.
Operator overloads should retain their mathematical/logical meaning.
Sources: [hidden](https://google.github.io/styleguide/rustguide.html#doc-hidden),
[const](https://google.github.io/styleguide/rustguide.html#const-functions),
[operators](https://google.github.io/styleguide/rustguide.html#operator-overloads).

## API-08 — Make required return-value use visible

Apply `#[must_use]` when ignoring a return prevents correct use, including
pure functions and critical/error information. A function returning a type
already marked `must_use` need not repeat it. Mark error-like types and lazy
computations when consuming the value is necessary.
Sources: [functions](https://google.github.io/styleguide/rustguide.html#must-use-on-functions),
[types](https://google.github.io/styleguide/rustguide.html#must-use-on-types).
