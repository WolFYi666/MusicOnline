/*
 Navicat Premium Dump SQL

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80040 (8.0.40)
 Source Host           : localhost:3306
 Source Schema         : musiconline

 Target Server Type    : MySQL
 Target Server Version : 80040 (8.0.40)
 File Encoding         : 65001

 Date: 28/04/2026 23:51:09
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin_users
-- ----------------------------
DROP TABLE IF EXISTS `admin_users`;
CREATE TABLE `admin_users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_admin_users_email`(`email` ASC) USING BTREE,
  UNIQUE INDEX `ix_admin_users_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of admin_users
-- ----------------------------
INSERT INTO `admin_users` VALUES (1, 'admin', 'admin@musiconline.com', 'musicOnline Admin', 'scrypt:32768:8:1$PdOkTA7uAlFFDohL$7573c5f4499fa63048ef2131c0128caf34520021ef562c56207185bae3eafa4f4b98776df167da6d081552f3c3c13b4eee6f2282056d2994402732e52ee65847', 1, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `admin_users` VALUES (2, 'moderator', 'moderator@musiconline.com', 'Content Moderator', 'scrypt:32768:8:1$EZjZ1vUI67spXeTl$5a1fa00d993750f0fa5849cb8a0f153fe3d7c89c3e3e8ecd67814712469496cfae3f42c585bad210a23b77d2e4cabb0ac396e393a045cf0c2d5ed90745f23018', 1, '2026-04-24 04:09:38', '2026-04-24 04:09:38');

-- ----------------------------
-- Table structure for customer_order_items
-- ----------------------------
DROP TABLE IF EXISTS `customer_order_items`;
CREATE TABLE `customer_order_items`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `seller_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10, 2) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_customer_order_items_seller_id`(`seller_id` ASC) USING BTREE,
  INDEX `ix_customer_order_items_product_id`(`product_id` ASC) USING BTREE,
  INDEX `ix_customer_order_items_order_id`(`order_id` ASC) USING BTREE,
  CONSTRAINT `customer_order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `customer_orders` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `customer_order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `music_listings` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `customer_order_items_ibfk_3` FOREIGN KEY (`seller_id`) REFERENCES `registered_users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of customer_order_items
-- ----------------------------
INSERT INTO `customer_order_items` VALUES (1, 1, 2, 1, 1, 216.00, '2026-04-24 04:15:46', '2026-04-24 04:15:46');
INSERT INTO `customer_order_items` VALUES (2, 2, 3, 2, 1, 205.00, '2026-04-24 04:22:00', '2026-04-24 04:22:00');
INSERT INTO `customer_order_items` VALUES (3, 3, 4, 2, 1, 118.00, '2026-04-24 04:22:00', '2026-04-24 04:22:00');
INSERT INTO `customer_order_items` VALUES (4, 4, 3, 2, 1, 205.00, '2026-04-24 04:30:29', '2026-04-24 04:30:29');
INSERT INTO `customer_order_items` VALUES (5, 5, 2, 1, 1, 216.00, '2026-04-24 04:32:53', '2026-04-24 04:32:53');
INSERT INTO `customer_order_items` VALUES (6, 6, 3, 2, 1, 205.00, '2026-04-24 04:37:48', '2026-04-24 04:37:48');
INSERT INTO `customer_order_items` VALUES (7, 7, 2, 1, 1, 216.00, '2026-04-24 04:50:09', '2026-04-24 04:50:09');

-- ----------------------------
-- Table structure for customer_orders
-- ----------------------------
DROP TABLE IF EXISTS `customer_orders`;
CREATE TABLE `customer_orders`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_number` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `buyer_id` int NOT NULL,
  `status` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_amount` decimal(10, 2) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_customer_orders_order_number`(`order_number` ASC) USING BTREE,
  INDEX `ix_customer_orders_status`(`status` ASC) USING BTREE,
  INDEX `ix_customer_orders_buyer_id`(`buyer_id` ASC) USING BTREE,
  CONSTRAINT `customer_orders_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `registered_users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of customer_orders
-- ----------------------------
INSERT INTO `customer_orders` VALUES (1, 'MO260424041545155', 2, 'created', 216.00, '2026-04-24 04:15:46', '2026-04-24 04:15:46');
INSERT INTO `customer_orders` VALUES (2, 'MO260424042159381', 1, 'created', 205.00, '2026-04-24 04:22:00', '2026-04-24 04:22:00');
INSERT INTO `customer_orders` VALUES (3, 'MO260424042159424', 1, 'created', 118.00, '2026-04-24 04:22:00', '2026-04-24 04:22:00');
INSERT INTO `customer_orders` VALUES (4, 'MO260424043029952', 1, 'created', 205.00, '2026-04-24 04:30:29', '2026-04-24 04:30:29');
INSERT INTO `customer_orders` VALUES (5, 'MO260424043252131', 2, 'created', 216.00, '2026-04-24 04:32:53', '2026-04-24 04:32:53');
INSERT INTO `customer_orders` VALUES (6, 'MO260424043747678', 1, 'created', 205.00, '2026-04-24 04:37:48', '2026-04-24 04:37:48');
INSERT INTO `customer_orders` VALUES (7, 'MO260424045008582', 2, 'created', 216.00, '2026-04-24 04:50:09', '2026-04-24 04:50:09');

-- ----------------------------
-- Table structure for music_categories
-- ----------------------------
DROP TABLE IF EXISTS `music_categories`;
CREATE TABLE `music_categories`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  UNIQUE INDEX `slug`(`slug` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of music_categories
-- ----------------------------
INSERT INTO `music_categories` VALUES (1, 'Rock Classics', 'rock-classics', 'Classic rock pressings, landmark albums, and essential guitar-led releases.', '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_categories` VALUES (2, 'Pop Essentials', 'pop-essentials', 'Pop albums, singles, and collector-friendly releases from defining artists.', '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_categories` VALUES (3, 'Soul & R&B', 'soul-rnb', 'Soul, R&B, and vocal records with rich arrangements and lasting appeal.', '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_categories` VALUES (4, 'Electronic & Dance', 'electronic-dance', 'Electronic, dance, and club-focused records for home listening or DJ shelves.', '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_categories` VALUES (5, 'Jazz Corner', 'jazz-corner', 'Jazz albums, reissues, and timeless recordings for focused collectors.', '2026-04-24 04:09:38', '2026-04-24 04:09:38');

-- ----------------------------
-- Table structure for music_listings
-- ----------------------------
DROP TABLE IF EXISTS `music_listings`;
CREATE TABLE `music_listings`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `artist` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `format_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `release_date` date NULL DEFAULT NULL,
  `price` decimal(10, 2) NOT NULL,
  `stock` int NOT NULL,
  `image_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `approval_status` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `seller_id` int NOT NULL,
  `category_id` int NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_music_listings_title`(`title` ASC) USING BTREE,
  INDEX `ix_music_listings_artist`(`artist` ASC) USING BTREE,
  INDEX `ix_music_listings_category_id`(`category_id` ASC) USING BTREE,
  INDEX `ix_music_listings_approval_status`(`approval_status` ASC) USING BTREE,
  INDEX `ix_music_listings_seller_id`(`seller_id` ASC) USING BTREE,
  CONSTRAINT `music_listings_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `registered_users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `music_listings_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `music_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 17 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of music_listings
-- ----------------------------
INSERT INTO `music_listings` VALUES (1, 'Rumours', 'Fleetwood Mac', 'album', 'A classic album with warm harmonies, polished production, and enduring appeal for rock collectors.', '1977-02-04', 188.00, 6, NULL, 'approved', 1, 1, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (2, 'The Dark Side of the Moon', 'Pink Floyd', 'album', 'A landmark progressive rock album known for immersive production and a highly collectible vinyl presence.', '1973-03-01', 216.00, 4, NULL, 'approved', 1, 1, '2026-04-24 04:09:38', '2026-04-24 04:50:09');
INSERT INTO `music_listings` VALUES (3, 'Abbey Road', 'The Beatles', 'album', 'A beloved Beatles release with iconic songwriting, detailed arrangements, and lasting collector demand.', '1969-09-26', 205.00, 4, NULL, 'approved', 2, 1, '2026-04-24 04:09:38', '2026-04-24 04:44:49');
INSERT INTO `music_listings` VALUES (4, 'Chronic Town', 'R.E.M.', 'ep', 'An early R.E.M. EP with jangly guitars, compact sequencing, and strong alternative-rock character.', '1982-08-24', 118.00, 9, NULL, 'approved', 2, 1, '2026-04-24 04:09:38', '2026-04-24 04:30:29');
INSERT INTO `music_listings` VALUES (5, 'Thriller', 'Michael Jackson', 'album', 'A defining pop album packed with signature singles, crisp production, and wide collector interest.', '1982-11-30', 198.00, 7, NULL, 'approved', 1, 2, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (6, '1989', 'Taylor Swift', 'album', 'A polished modern pop release with bright production, strong hooks, and broad audience appeal.', '2014-10-27', 176.00, 9, NULL, 'approved', 2, 2, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (7, 'Take On Me', 'a-ha', 'single', 'A bright synth-pop single with an instantly recognizable chorus and strong eighties nostalgia.', '1985-10-19', 92.00, 12, NULL, 'approved', 2, 2, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (8, 'Future Nostalgia', 'Dua Lipa', 'album', 'A dance-pop album with glossy production, disco influence, and strong demand among modern collectors.', '2020-03-27', 182.00, 7, NULL, 'pending', 1, 2, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (9, 'Back to Black', 'Amy Winehouse', 'album', 'A modern soul classic with expressive vocals, sharp songwriting, and a distinctive retro tone.', '2006-10-27', 184.00, 6, NULL, 'approved', 1, 3, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (10, 'Songs in the Key of Life', 'Stevie Wonder', 'album', 'A sweeping Stevie Wonder album with rich arrangements, deep grooves, and premium collector appeal.', '1976-09-28', 238.00, 3, NULL, 'approved', 2, 3, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (11, 'My Dear Melancholy,', 'The Weeknd', 'ep', 'A moody R&B EP with atmospheric production, concise sequencing, and late-night listening appeal.', '2018-03-30', 126.00, 8, NULL, 'approved', 2, 3, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (12, 'Random Access Memories', 'Daft Punk', 'album', 'A sleek electronic album blending live instrumentation, dance-floor energy, and audiophile-friendly production.', '2013-05-17', 214.00, 5, NULL, 'approved', 1, 4, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (13, 'Discovery', 'Daft Punk', 'album', 'A colorful Daft Punk release filled with French house textures, playful hooks, and club-era nostalgia.', '2001-03-12', 172.00, 7, NULL, 'approved', 2, 4, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (14, 'Midnight City', 'M83', 'single', 'A widescreen synth-pop single with a soaring hook, pulsing rhythm, and cinematic energy.', '2011-08-16', 88.00, 10, NULL, 'rejected', 1, 4, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (15, 'Kind of Blue', 'Miles Davis', 'album', 'A definitive modal jazz recording with relaxed interplay, elegant solos, and essential collector status.', '1959-08-17', 168.00, 8, NULL, 'approved', 2, 5, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `music_listings` VALUES (16, 'Blue Train', 'John Coltrane', 'album', 'A focused hard-bop session led by John Coltrane with rich tone, drive, and classic Blue Note character.', '1958-01-01', 158.00, 7, NULL, 'approved', 1, 5, '2026-04-24 04:09:38', '2026-04-24 04:09:38');

-- ----------------------------
-- Table structure for registered_users
-- ----------------------------
DROP TABLE IF EXISTS `registered_users`;
CREATE TABLE `registered_users`  (
  `is_retailer` tinyint(1) NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_registered_users_email`(`email` ASC) USING BTREE,
  UNIQUE INDEX `ix_registered_users_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of registered_users
-- ----------------------------
INSERT INTO `registered_users` VALUES (1, 1, 'vinylnova', 'vinylnova@musiconline.com', 'Vinyl Nova Records', 'scrypt:32768:8:1$LJn6KpNRD6dcUcBk$16dca2f0e69c5d9b22f4a9ec892d43b6f059a89c8cf326c972dd26fff4ad64339196fca5f27a71f4a847b8f68720276e9e0d2edd9e236a67e82c9d9afdea12b3', 1, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `registered_users` VALUES (0, 2, 'analogsoul', 'analogsoul@musiconline.com', 'Analog Soul Collector', 'scrypt:32768:8:1$moG3ijvl1PE03cuj$eecf9d773b47c83fba1458c1f60c0a7ea807f72933b9616835cf35c8f7425eaa95670b8bcdc1bca129ea83f131981a2f0b744842cf8508dc50262285ffebdcbd', 1, '2026-04-24 04:09:38', '2026-04-24 04:09:38');
INSERT INTO `registered_users` VALUES (0, 3, 'popupuser', 'popupuser@musiconline.com', 'Popup User', 'scrypt:32768:8:1$zXporREdwO7HTaEq$20690773bfed6daf0e76bfab8d75cc21b7be55fcb05ba09999df17112c1ee9da8ece3d8c6c7cf690a8d2c02fcd1e9e6613263d918be90c7d0d853c3cfca4c1b8', 1, '2026-04-24 04:21:59', '2026-04-24 04:21:59');

-- ----------------------------
-- Table structure for shopping_cart_items
-- ----------------------------
DROP TABLE IF EXISTS `shopping_cart_items`;
CREATE TABLE `shopping_cart_items`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `buyer_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_shopping_cart_item_buyer_product`(`buyer_id` ASC, `product_id` ASC) USING BTREE,
  INDEX `ix_shopping_cart_items_product_id`(`product_id` ASC) USING BTREE,
  INDEX `ix_shopping_cart_items_buyer_id`(`buyer_id` ASC) USING BTREE,
  CONSTRAINT `shopping_cart_items_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `registered_users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `shopping_cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `music_listings` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of shopping_cart_items
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
