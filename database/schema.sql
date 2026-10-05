-- ============================================================================
-- Intelligent Health Management Platform - MySQL schema (7 tables)
-- The running app creates its tables via SQLAlchemy (db.create_all());
-- this script is the reference DDL for the thesis and for manual setups.
--   mysql -u root -p < schema.sql
-- ============================================================================

CREATE DATABASE IF NOT EXISTS health_platform
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE health_platform;

-- 1. users ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  username      VARCHAR(50)  NOT NULL,
  email         VARCHAR(120) NOT NULL,
  password_hash VARCHAR(256) NOT NULL,
  height        FLOAT        NULL COMMENT 'cm',
  weight        FLOAT        NULL COMMENT 'kg',
  age           INT          NULL,
  gender        VARCHAR(10)  NULL COMMENT 'male / female / other',
  created_at    DATETIME     NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_username (username),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. goals (users 1:N goals) ---------------------------------------------
CREATE TABLE IF NOT EXISTS goals (
  id                   INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id              INT UNSIGNED NOT NULL,
  goal_type            VARCHAR(20)  NOT NULL COMMENT 'lose / gain / maintain',
  target_weight        FLOAT        NULL COMMENT 'kg',
  daily_calorie_target INT          NULL,
  start_date           DATE         NOT NULL,
  end_date             DATE         NOT NULL,
  PRIMARY KEY (id),
  KEY idx_goals_user (user_id),
  CONSTRAINT fk_goals_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. foods (reference database) -------------------------------------------
CREATE TABLE IF NOT EXISTS foods (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name         VARCHAR(100) NOT NULL,
  category     VARCHAR(30)  NOT NULL,
  calories     FLOAT        NOT NULL COMMENT 'kcal per serving',
  protein      FLOAT        NOT NULL COMMENT 'g per serving',
  carbs        FLOAT        NOT NULL COMMENT 'g per serving',
  fat          FLOAT        NOT NULL COMMENT 'g per serving',
  serving_size VARCHAR(50)  NULL,
  PRIMARY KEY (id),
  KEY idx_foods_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. exercises (reference database) ---------------------------------------
CREATE TABLE IF NOT EXISTS exercises (
  id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name      VARCHAR(100) NOT NULL,
  category  VARCHAR(30)  NOT NULL COMMENT 'cardio / strength / flexibility / sports',
  met_value FLOAT        NOT NULL,
  PRIMARY KEY (id),
  KEY idx_exercises_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. meal_logs (users 1:N, meal_logs N:1 foods) ---------------------------
CREATE TABLE IF NOT EXISTS meal_logs (
  id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id   INT UNSIGNED NOT NULL,
  food_id   INT UNSIGNED NOT NULL,
  meal_type VARCHAR(20)  NOT NULL COMMENT 'breakfast / lunch / dinner / snack',
  quantity  FLOAT        NOT NULL DEFAULT 1 COMMENT 'number of servings',
  log_date  DATE         NOT NULL,
  PRIMARY KEY (id),
  KEY idx_meal_logs_user_date (user_id, log_date),
  CONSTRAINT fk_meal_logs_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  CONSTRAINT fk_meal_logs_food FOREIGN KEY (food_id) REFERENCES foods (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. workout_logs (users 1:N, workout_logs N:1 exercises) ------------------
CREATE TABLE IF NOT EXISTS workout_logs (
  id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id         INT UNSIGNED NOT NULL,
  exercise_id     INT UNSIGNED NOT NULL,
  duration_min    INT          NOT NULL COMMENT 'minutes',
  intensity       VARCHAR(20)  NOT NULL DEFAULT 'moderate',
  calories_burned FLOAT        NOT NULL,
  log_date        DATE         NOT NULL,
  PRIMARY KEY (id),
  KEY idx_workout_logs_user_date (user_id, log_date),
  CONSTRAINT fk_workout_logs_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  CONSTRAINT fk_workout_logs_exercise FOREIGN KEY (exercise_id) REFERENCES exercises (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. recommendations (users 1:N, explainable via `reason`) -----------------
CREATE TABLE IF NOT EXISTS recommendations (
  id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id    INT UNSIGNED NOT NULL,
  rec_type   VARCHAR(20)  NOT NULL COMMENT 'meal / workout',
  item_id    INT UNSIGNED NOT NULL COMMENT 'foods.id or exercises.id',
  score      FLOAT        NULL COMMENT 'similarity / ranking score',
  reason     VARCHAR(255) NOT NULL,
  created_at DATETIME     NULL,
  PRIMARY KEY (id),
  KEY idx_recommendations_user (user_id),
  CONSTRAINT fk_recommendations_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
