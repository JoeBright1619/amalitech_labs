# Lab 2: Social Media Platform Data Backend

## Overview

**Assessment**: Database Fundamentals  
**Complexity**: Medium  
**Estimated Time**: 6-10 hours

## Objectives

- Design a normalized schema for a social media application.
- Use `psycopg2` for transactional operations like following a user.
- Combine SQL and NoSQL to handle different data types effectively.
- Write complex queries to build a user's feed or find trending posts.
- Analyze and optimize query performance for a high-read environment.

## Description

Build the data backend for a social media platform. You will design a normalized PostgreSQL schema for users, posts, comments, and followers. Python scripts will handle user interactions like creating posts and following users transactionally. You'll use Redis to cache user timelines, MongoDB for activity logs, and PostgreSQL's JSONB for post metadata. The main challenge will be to write and optimize the complex queries needed to generate a user's feed.

## Implementation Details

- **Modeling**: Design a 3NF schema for users, posts, comments, and a followers join table. Create an ER diagram.
- **Python Connectivity**: Use `psycopg2` and a connection pool. The "follow user" action must be a transaction that updates two tables atomically. Use parameterized queries everywhere.
- **SQL & NoSQL Integration**:
  - **PostgreSQL**: Store post metadata like tags or location in a JSONB column.
  - **Redis**: Cache the generated timeline for each user to reduce database load.
  - **MongoDB**: Store unstructured activity stream data (e.g., "User A liked Post B").
- **Complex Queries & Performance**:
  - Write a query with CTEs and JOINs to generate a user's timeline (posts from people they follow).
  - Use a window function (`ROW_NUMBER()`) for stable pagination.
  - Use `EXPLAIN ANALYZE` to diagnose the performance of the feed generation query.
  - Add composite B-tree indexes (e.g., on the followers table) to drastically improve performance.

## Grading Criteria

1. **Feature Implementation (20)**: All data operations and integrations (SQL, NoSQL) are functional.
2. **Code Quality & Structure (15)**: Python code is clean, modular, and uses parameterized queries correctly.
3. **Best Practices & Patterns (15)**: Correct normalization, ACID transactions, and effective use of caching.
4. **Testing & Validation (20)**: Queries produce correct results; performance optimizations are verified.
5. **Documentation & Comments (10)**: Clear ER diagram, README explains design choices and optimization results.
6. **Final Integration & Output Quality (20)**: The entire data pipeline is functional, from insertion to complex querying.
