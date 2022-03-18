SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `fee` (
  `order_id` varchar(26) NOT NULL,
  `final_value_fee` decimal(4,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `feedback` (
  `feedback_id` varchar(13) NOT NULL,
  `legacy_order_id` varchar(255) NOT NULL,
  `feedback_type` set('Negative','Neutral','Positive','Withdrawn') NOT NULL,
  `comment` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `fulfillment` (
  `order_id` varchar(26) NOT NULL,
  `buyer_name` varchar(64) NOT NULL,
  `address_line_1` varchar(64) NOT NULL,
  `city` varchar(128) NOT NULL,
  `county` varchar(64) NOT NULL,
  `post_code` varchar(9) NOT NULL,
  `country_code` char(2) NOT NULL,
  `fulfillment_method` varchar(64) DEFAULT NULL,
  `fulfillment_cost` decimal(6,2) DEFAULT NULL,
  `tracking_id` varchar(32) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `line` (
  `line_item_id` bigint(14) UNSIGNED NOT NULL,
  `order_id` varchar(26) NOT NULL,
  `item_id` varchar(20) NOT NULL,
  `title` varchar(80) NOT NULL,
  `sale_format` set('AUCTION','FIXED_PRICE','OTHER','SECOND_CHANCE_OFFER') NOT NULL,
  `quantity` tinyint(3) UNSIGNED NOT NULL,
  `fulfillment_status` set('FULFILLED','IN_PROGRESS','NOT_STARTED','') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `payment` (
  `line_item_id` bigint(14) UNSIGNED NOT NULL,
  `transaction_id` int(4) NOT NULL,
  `payment_date` datetime NOT NULL,
  `payment_status` set('FAILED','FULLY_REFUNDED','PAID','PARTIALLY_REFUNDED','PENDING') NOT NULL,
  `currency` varchar(3) NOT NULL,
  `item_cost` decimal(6,2) NOT NULL,
  `postage_cost` decimal(6,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `transaction` (
  `transaction_id` int(4) NOT NULL,
  `processor_name` set('PAYPAL','EBAY') NOT NULL DEFAULT 'PAYPAL',
  `processor_id` varchar(17) NOT NULL,
  `transaction_date` datetime NOT NULL,
  `transaction_amount` decimal(6,2) NOT NULL DEFAULT 0.00,
  `transaction_currency` varchar(3) NOT NULL DEFAULT 'GBP',
  `fee_amount` decimal(5,2) NOT NULL DEFAULT 0.00,
  `fee_currency` varchar(3) NOT NULL DEFAULT 'GBP',
  `transaction_status` char(1) DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `sale` (
  `order_id` varchar(26) NOT NULL,
  `legacy_order_id` varchar(26) NOT NULL,
  `sale_date` datetime NOT NULL,
  `buyer_username` varchar(64) NOT NULL,
  `status` set('FULFILLED','IN_PROGRESS','NOT_STARTED','') NOT NULL,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


ALTER TABLE `fee`
  ADD PRIMARY KEY (`order_id`);

ALTER TABLE `feedback`
  ADD PRIMARY KEY (`feedback_id`),
  ADD KEY `feedback_legacy_order_id` (`legacy_order_id`);

ALTER TABLE `fulfillment`
  ADD PRIMARY KEY (`order_id`);

ALTER TABLE `line`
  ADD PRIMARY KEY (`line_item_id`),
  ADD KEY `line_order_id` (`order_id`);

ALTER TABLE `payment`
  ADD PRIMARY KEY (`line_item_id`);
  ADD KEY `transaction_transaction_id` (`transaction_id`);

ALTER TABLE `sale`
  ADD PRIMARY KEY (`order_id`),
  ADD UNIQUE KEY `legacy_order_id` (`legacy_order_id`);

ALTER TABLE `transaction`
  ADD PRIMARY KEY (`transaction_id`),
  ADD UNIQUE KEY `processor_id` (`processor_id`);

ALTER TABLE `transaction`
  MODIFY `transaction_id` int(4) NOT NULL AUTO_INCREMENT;


ALTER TABLE `fee`
  ADD CONSTRAINT `fee_order_id` FOREIGN KEY (`order_id`) REFERENCES `sale` (`order_id`) ON UPDATE CASCADE;

ALTER TABLE `feedback`
  ADD CONSTRAINT `feedback_legacy_order_id` FOREIGN KEY (`legacy_order_id`) REFERENCES `sale` (`legacy_order_id`) ON UPDATE CASCADE;

ALTER TABLE `fulfillment`
  ADD CONSTRAINT `fulfillment_order_id` FOREIGN KEY (`order_id`) REFERENCES `sale` (`order_id`) ON UPDATE CASCADE;

ALTER TABLE `payment`
  ADD CONSTRAINT `payment_line_item_id` FOREIGN KEY (`line_item_id`) REFERENCES `line` (`line_item_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `transaction_transaction_id` FOREIGN KEY (`transaction_id`) REFERENCES `transaction` (`transaction_id`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
