// == PREAMBLE ================================================

// * Licensed under the Apache License, Version 2.0; see README

/*
 * Range.hpp
 *
 *  Created on: Aug 14, 2014
 *      Author: JKM
 */

#ifndef rrRangeH
#define rrRangeH

// == INCLUDES ================================================

#include <type_traits>

// == CODE ====================================================

namespace rr
{

/**
 * @author JKM
 * @brief Allows iterating over a range,
 * defined by a begin / end iterator pair
 * @details Use this class with a pair of begin/end iterators.
 * The result is an object
 * with the usual begin/end iterator semantics, which enables
 * use within range-based for loops, among other things.
 * This is typically used to wrap iterator functions which may
 * have names other than begin & end, or to allow iterating
 * over a container with multiple types of elements, as the
 * following example shows.
 * @verbat
 * // example usage
 * class graph {
 *     // node iterators
 *     node_iterator nodes_begin();
 *     node_iterator nodes_end();\n
 *     // return a range of all nodes
 *     Range<graph::node_iterator> nodes() {
 *         return Range<graph::node_iterator>(g.nodes_begin(), g.nodes_end());
 *     }\n
 *     // edge iterators
 *     edge_iterator edges_begin();
 *     edge_iterator edges_end();\n
 *     // return a range of all edges
 *     Range<graph::edge_iterator> edges() {
 *         return Range<graph::edge_iterator>(g.edges_begin(), g.edges_end());
 *     }\n
 * };\n
 * // the type graph has no begin/end functions and therefore cannot
 * // be used in a range-based for, but its range methods can
 * graph g;\n
 * // loop over nodes
 * for (node n : g.nodes())
 *     std::cout << n << std::endl;\n
 * // loop over edges
 * for (edge e : g.edges())
 *     std::cout << e << std::endl;
 * @endverbat
 */
template <class Iterator>
class Range {
public:
    typedef Iterator IteratorType;
    typedef Iterator iterator;

    /** @brief Construct directly from begin/end iterators
     * @details Supply the iterator pair when using this constructor, e.g.
     * @verbat
     * std::vector<int> vec;
     * vec.push_back(1);
     * for (int i : range(vec.begin(), vec.end())) {}
     * @endverbat
     */
    Range(IteratorType begin, IteratorType end)
        : begin_(begin), end_(end) {}

    /// Construct from container @ref c with begin/end methods
    template<class Contiainer>
    Range(Contiainer& c)
        : begin_(c.begin()), end_(c.end()) {}

    /// Construct from container @ref c with begin/end methods
    template<class Contiainer>
    Range(const Contiainer& c)
        : begin_(c.begin()), end_(c.end()) {}

    /// Required begin func
    IteratorType begin() { return begin_; }
    /// Required end func
    IteratorType end() { return end_; }

protected:
    IteratorType begin_, end_;
};

} // namespace rr

#endif // rrAccessPtrIterH
