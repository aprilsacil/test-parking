-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 24, 2024 at 10:39 PM
-- Server version: 5.7.43
-- PHP Version: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `parking`
--
CREATE DATABASE IF NOT EXISTS `parking` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `parking`;

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` int(10) UNSIGNED NOT NULL,
  `ticket_route` varchar(10) NOT NULL,
  `ticket_location` varchar(255) NOT NULL,
  `ticket_coordinates` point NOT NULL,
  `ticket_issue_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ticket_agency` varchar(10) NOT NULL,
  `ticket_meter_id` varchar(10) DEFAULT NULL,
  `ticket_marked_time` time DEFAULT NULL,
  `violation_id` int(10) UNSIGNED NOT NULL,
  `vehicle_id` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `vehicle`
--

CREATE TABLE `vehicle` (
  `vehicle_id` int(10) UNSIGNED NOT NULL,
  `vehicle_make` varchar(10) NOT NULL,
  `vehicle_body` varchar(10) NOT NULL,
  `vehicle_color` varchar(10) NOT NULL,
  `vehicle_plate_expiry` varchar(11) DEFAULT NULL,
  `vehicle_vin` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `violation`
--

CREATE TABLE `violation` (
  `violation_id` int(10) UNSIGNED NOT NULL,
  `violation_code` varchar(255) NOT NULL,
  `violation_description` varchar(255) DEFAULT NULL,
  `violation_state` varchar(5) NOT NULL,
  `violation_fine` float(10,2) NOT NULL DEFAULT '0.00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`),
  ADD KEY `ticket_route` (`ticket_route`),
  ADD KEY `ticket_location` (`ticket_location`),
  ADD KEY `ticket_issue_date` (`ticket_issue_datetime`),
  ADD KEY `ticket_agency` (`ticket_agency`),
  ADD SPATIAL KEY `ticket_coordinates` (`ticket_coordinates`),
  ADD KEY `FK_ticketVehicle` (`vehicle_id`),
  ADD KEY `FK_ticketViolation` (`violation_id`);

--
-- Indexes for table `vehicle`
--
ALTER TABLE `vehicle`
  ADD PRIMARY KEY (`vehicle_id`),
  ADD KEY `vehicle_make` (`vehicle_make`);

--
-- Indexes for table `violation`
--
ALTER TABLE `violation`
  ADD PRIMARY KEY (`violation_id`),
  ADD KEY `violation_code` (`violation_code`),
  ADD KEY `violation_description` (`violation_description`),
  ADD KEY `violation_state` (`violation_state`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ticket`
--
ALTER TABLE `ticket`
  MODIFY `ticket_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `vehicle`
--
ALTER TABLE `vehicle`
  MODIFY `vehicle_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `violation`
--
ALTER TABLE `violation`
  MODIFY `violation_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `FK_ticketVehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle` (`vehicle_id`),
  ADD CONSTRAINT `FK_ticketViolation` FOREIGN KEY (`violation_id`) REFERENCES `violation` (`violation_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
