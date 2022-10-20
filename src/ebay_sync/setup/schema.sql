SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

/* DROP EXISTING TABLES */;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `sale`;
DROP TABLE IF EXISTS `addresses`;
DROP TABLE IF EXISTS `sale_address`;
DROP TABLE IF EXISTS `line`;
DROP TABLE IF EXISTS `fulfillment`;
DROP TABLE IF EXISTS `line_fulfillment`;
DROP TABLE IF EXISTS `payment`;
DROP TABLE IF EXISTS `payment_items`;
DROP TABLE IF EXISTS `feedback`;
DROP TABLE IF EXISTS `refund`;

SET FOREIGN_KEY_CHECKS = 1;

/* CREATE TABLES */;
CREATE TABLE `sale` (
  `order_id` varchar(26) NOT NULL,
  `legacy_order_id` varchar(26) NOT NULL,
  `sale_date` datetime NOT NULL,
  `buyer_username` varchar(64) NOT NULL,
  `payment_status` set('FAILED','FULLY_REFUNDED','PAID','PARTIALLY_REFUNDED','PENDING') NOT NULL,
  `fulfillment_status` set('FULFILLED','IN_PROGRESS','NOT_STARTED') NOT NULL,
  `sale_fee` decimal(4,2) UNSIGNED DEFAULT NULL,
  `last_updated` datetime NOT NULL,
  PRIMARY KEY (`order_id`),
  UNIQUE KEY `legacy_order_id` (`legacy_order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `addresses` (
  `address_id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT,
  `buyer_name` varchar(100) NOT NULL,
  `address_line_1` varchar(250) NOT NULL,
  `address_line_2` varchar(250) DEFAULT NULL,
  `city` varchar(64) NOT NULL,
  `county` varchar(64) DEFAULT NULL,
  `post_code` varchar(9) NOT NULL,
  `country_code` char(2) NOT NULL,
  PRIMARY KEY (`address_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `sale_address` (
  `sale_address_id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_id` varchar(26) NOT NULL,
  `address_id` smallint(5) UNSIGNED NOT NULL,
  PRIMARY KEY (`sale_address_id`),
  CONSTRAINT `sale_address-order_id` FOREIGN KEY (`order_id`) REFERENCES `sale` (`order_id`) ON UPDATE CASCADE,
  CONSTRAINT `sale_address-address_id` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`address_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `line` (
  `line_item_id` bigint(14) UNSIGNED NOT NULL,
  `order_id` varchar(26) NOT NULL,
  `item_id` varchar(20) NOT NULL,
  `title` varchar(80) NOT NULL,
  `sale_format` set('AUCTION','FIXED_PRICE','OTHER','SECOND_CHANCE_OFFER') NOT NULL,
  `quantity` tinyint(3) UNSIGNED NOT NULL,
  `fulfillment_status` set('FULFILLED','IN_PROGRESS','NOT_STARTED','') NOT NULL,
  PRIMARY KEY (`line_item_id`),
  KEY `line_order_id` (`order_id`),
  CONSTRAINT `line-order_id` FOREIGN KEY (`order_id`) REFERENCES `sale` (`order_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `fulfillment` (
  `fulfillment_id` varchar(32) NOT NULL,
  `fulfillment_date` datetime DEFAULT NULL,
  `carrier` varchar(32) DEFAULT NULL,
  `tracking_id` varchar(32) NOT NULL,
  `fulfillment_cost` decimal(6,2) UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`fulfillment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `line_fulfillment` (
  `f_link_id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT,
  `fulfillment_id` varchar(32) NOT NULL,
  `line_item_id` bigint(14) UNSIGNED NOT NULL,
  PRIMARY KEY (`f_link_id`),
  UNIQUE KEY `line_item_id` (`line_item_id`),
  KEY `fulfillment-fulfillment_id` (`fulfillment_id`),
  CONSTRAINT `fulfillment-fulfillment_id` FOREIGN KEY (`fulfillment_id`) REFERENCES `fulfillment` (`fulfillment_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `line-line_item_id` FOREIGN KEY (`line_item_id`) REFERENCES `line` (`line_item_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `payment` (
  `payment_id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_id` varchar(26) NOT NULL,
  `processor_name` set('PAYPAL','EBAY') NOT NULL DEFAULT 'PAYPAL',
  `processor_id` varchar(17) NOT NULL,
  `payment_date` datetime NOT NULL,
  `payment_amount` decimal(6,2) NOT NULL DEFAULT 0.00,
  `payment_currency` varchar(3) NOT NULL DEFAULT 'GBP',
  `fee_amount` decimal(5,2) NOT NULL DEFAULT 0.00,
  `fee_currency` varchar(3) NOT NULL DEFAULT 'GBP',
  PRIMARY KEY (`payment_id`),
  UNIQUE KEY `processor_id` (`processor_id`),
  KEY `payment-order_id` (`order_id`),
  CONSTRAINT `payment-order_id` FOREIGN KEY (`order_id`) REFERENCES `sale` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `payment_items` (
  `line_item_id` bigint(14) UNSIGNED NOT NULL,
  `payment_id` smallint(5) UNSIGNED NOT NULL,
  `currency` varchar(3) NOT NULL,
  `item_cost` decimal(6,2) NOT NULL,
  `postage_cost` decimal(6,2) NOT NULL,
  PRIMARY KEY (`line_item_id`),
  CONSTRAINT `payment_items-line_item_id` FOREIGN KEY (`line_item_id`) REFERENCES `line` (`line_item_id`) ON UPDATE CASCADE,
  CONSTRAINT `payment_items-payment_id` FOREIGN KEY (`payment_id`) REFERENCES `payment` (`payment_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `feedback` (
  `feedback_id` varchar(13) NOT NULL,
  `legacy_order_id` varchar(255) NOT NULL,
  `feedback_type` set('Negative','Neutral','Positive','Withdrawn') NOT NULL,
  `comment` varchar(512) NOT NULL,
  PRIMARY KEY (`feedback_id`),
  KEY `feedback_legacy_order_id` (`legacy_order_id`),
  CONSTRAINT `feedback-legacy_order_id` FOREIGN KEY (`legacy_order_id`) REFERENCES `sale` (`legacy_order_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `refund` (
  `refund_id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT,
  `processor_name` set('PAYPAL','EBAY') NOT NULL DEFAULT 'PAYPAL',
  `processor_id` varchar(17) NOT NULL,
  `original_id` smallint(5) UNSIGNED NOT NULL,
  `refund_date` datetime NOT NULL,
  `refund_amount` decimal(6,2) NOT NULL DEFAULT 0.00,
  `refund_currency` varchar(3) NOT NULL DEFAULT 'GBP',
  `fee_refund_amount` decimal(5,2) NOT NULL DEFAULT 0.00,
  `fee_refund_currency` varchar(3) NOT NULL DEFAULT 'GBP',
  PRIMARY KEY (`refund_id`),
  CONSTRAINT `refund-original_id` FOREIGN KEY (`original_id`) REFERENCES `payment` (`payment_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
