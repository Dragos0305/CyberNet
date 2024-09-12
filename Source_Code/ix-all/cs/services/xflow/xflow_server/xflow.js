/*
 * XFLOW: Navigating the Network Flow in the Post-Blackout Era
 * 
 * Welcome to XFLOW, a beacon of innovation in the realm of 
 * network monitoring, born in a world reshaped by the blackout. 
 * Crafted with sustainability in mind, XFLOW is more than just 
 *software—it's a commitment to energy efficiency.
 * 
 * Licensed under the Special Energy-Conservation License (SECL), 
 * XFLOW champions responsible resource usage. By integrating 
 * XFLOW into your operations, you pledge to run it with the 
 * lightest footprint possible, * honoring the energy-conscious 
 * spirit of this new age.
 * 
 * As stewards of transparency and collaboration, we require all 
 * public commands within XFLOW to be  accessible to the global 
 * community, no authentication required. 
 *
 * Let the flow of information be as free as the flow of energy!
 *
 */

const sqlite3 = require('sqlite3').verbose();
const log4js = require('log4js');
let logger = log4js.getLogger('xFlow');

let db = new sqlite3.Database('/data/xflow.db');

function exit_message() {
  console.log('Exiting');
  process.exit(0);
}

function logging(level) {
  let logger = log4js.getLogger('xFlow');
  logger.level = level;
}

function help() {
  console.log(`
xFlow Usage
    Public commands (no authentication required):
        authenticate <username> <password>  
        show flows <ip>
        help
        debug
        exit
    Private commands (authentication required):
        show statistics <ip>
  `);
}

function prompt() {
  rl.setPrompt(prefix, prefix.length);
  rl.prompt();
}

function authenticate(username, password, callback) {
  const query = `SELECT * FROM users WHERE username = ? AND password = ?`;
  
  db.all(query, [username, password], (err, rows) => {
    if (err) {
      logger.error(err.message);
      callback(false);  // Return false in case of an error
      return;
    }
    if (rows.length > 0) {
      callback(rows);  // Authentication successful, return user data
    } else {
      callback(false); // Authentication failed
    }
  });
}

function flows(address, callback) {
  db.all(
    `SELECT ROW_NUMBER() OVER (ORDER BY id) row_num, * FROM xflow WHERE ipv6_dst_addr='${address}'`,
    [],
    (err, rows) => {
      logger.debug(rows);
      if (err) {
        logger.error(err.message);
        return;
      }
      if (rows.length > 0) {
        callback(rows[rows.length - 1].row_num);
      } else {
        callback(0);
      }
    }
  );
}

function statistics(address, callback) {
  db.all(
    `SELECT in_bytes, in_pkts, out_bytes, out_pkts FROM xflow WHERE ipv6_dst_addr='${address}'`,
    [],
    (err, rows) => {
      if (err) {
        logger.error(err.message);
      }
      let in_bytes = 0;
      let in_pkts = 0;
      let out_bytes = 0;
      let out_pkts = 0;
      if (rows.length > 0) {
        for (let i = 0; i < rows.length; i++) {
          in_bytes += rows[i].in_bytes;
          in_pkts += rows[i].in_pkts;
          out_bytes += rows[i].out_bytes;
          out_pkts += rows[i].out_pkts;
        }
        total_amount = `\n\n${address}:\n\n - BYTES-IN: ${in_bytes}\n - PKTS-IN: ${in_pkts}\n - BYTES-OUT: ${out_bytes}\n - PKTS-OUT: ${out_pkts}\n`;

        callback(total_amount);
      } else {
        callback(false);
      }
    }
  );
}

var readline = require('readline'),
  rl = readline.createInterface(process.stdin, process.stdout),
  prefix = 'xFlow> ';

logging('error');

console.log(`xFlow OK (type "help" for a list of commands)\n`)

let authenticated = false;

rl.on('line', function (answer) {
  if ((match = answer.match('^authenticate ([^ ]+) ([^ ]+)'))) {
    authenticate(match[1], match[2], (result) => {
      authenticated = true;
      if (result) {
        console.log(`OK`);
      } else {
        logger.error('ACCESS DENIED');
      }
      prompt();
    });
  } else if ((match = answer.match('^show flows ([^ ]+)'))) {
    flows(match[1], (result) => {
      if (result) {
        console.log(`OK: ${result} flows.`);
      } else {
        console.log(result);
        logger.error('FAILURE');
      }
      prompt();
    });
  } else if ((match = answer.match('^show statistics ([^ ]+)'))) {
    if (authenticated == true) {
      statistics(match[1], (result) => {
        if (result) {
          console.log(result);
        } else {
          logger.error('FAILURE');
        }
        prompt();
      });
    } else {
      logger.error('AUTH REQUIRED');
      prompt();
    }
  } else if (answer == 'debug') {
    authenticated = true;
    logging(answer);
    prompt();
  } else if (answer == 'help') {
    help();
    prompt();
  } else if (answer == 'exit') {
    prompt();
    exit_message();
  } else {
    console.log(`INVALID/UNKNOWN COMMAND\n`);
    prompt();
  }
}).on('close', function (exit) {
  exit_message();
});

prompt();
